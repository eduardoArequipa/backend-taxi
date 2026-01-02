from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from PIL import Image
import os
import uuid
import io

from database.database import get_db
from schemas.vehiculo import Vehiculo, VehiculoCreate, VehiculoUpdate
from repository import vehiculo as repository_vehiculo
from repository import usuario as repository_usuario
from api.dependencies import get_current_user, get_current_operador
from schemas.usuario import User
from models.enums import RolUsuario

router = APIRouter()

# Directorio para guardar imágenes
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "vehiculos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

# Tamaño máximo de archivo (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def optimize_image_to_webp(image_data: bytes, max_size: tuple = (1200, 1200), quality: int = 85) -> bytes:
    """
    Optimiza una imagen convirtiéndola a formato WebP.
    - Redimensiona si excede max_size manteniendo proporción
    - Comprime con la calidad especificada
    """
    image = Image.open(io.BytesIO(image_data))

    # Convertir a RGB si tiene canal alpha (excepto si es necesario)
    if image.mode in ('RGBA', 'LA', 'P'):
        # Crear fondo blanco para imágenes con transparencia
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # Redimensionar si excede el tamaño máximo
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Guardar como WebP
    output = io.BytesIO()
    image.save(output, format='WEBP', quality=quality, optimize=True)
    output.seek(0)

    return output.getvalue()


class VehiculoAsignar(BaseModel):
    """Schema para que operadores asignen vehiculos a conductores"""
    marca: str
    modelo: str
    placa: str
    color: str
    anio: Optional[int] = None
    conductor_id: int


@router.post("/", response_model=Vehiculo, status_code=201)
def create_new_vehiculo(
    vehiculo: VehiculoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo vehículo. Solo los conductores pueden crear vehículos.
    El vehículo se asigna automáticamente al conductor autenticado.
    """
    if current_user.rol != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden registrar vehículos.")

    return repository_vehiculo.create_vehiculo(db=db, vehiculo=vehiculo, conductor_id=current_user.id)


@router.post("/asignar", response_model=Vehiculo, status_code=201)
def asignar_vehiculo_a_conductor(
    vehiculo: VehiculoAsignar,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operador)
):
    """
    Asigna un vehículo a un conductor. Solo operadores pueden usar este endpoint.
    """
    # Verificar que el conductor existe y es conductor
    conductor = repository_usuario.get_user_by_id(db, vehiculo.conductor_id)
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    if conductor.rol != RolUsuario.conductor:
        raise HTTPException(status_code=400, detail="El usuario no es un conductor")

    # Crear el vehículo
    vehiculo_data = VehiculoCreate(
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        placa=vehiculo.placa,
        color=vehiculo.color
    )
    return repository_vehiculo.create_vehiculo(db=db, vehiculo=vehiculo_data, conductor_id=vehiculo.conductor_id)


@router.get("/", response_model=List[Vehiculo])
def read_all_vehiculos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operador)
):
    """
    Obtiene todos los vehículos. Solo operadores.
    """
    return repository_vehiculo.get_all_vehiculos(db, skip=skip, limit=limit)

@router.get("/me", response_model=List[Vehiculo])
def read_my_vehiculos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de vehículos del conductor autenticado.
    """
    if current_user.rol != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a este endpoint.")
    return repository_vehiculo.get_vehiculos_by_conductor(db, conductor_id=current_user.id)

@router.get("/{vehiculo_id}", response_model=Vehiculo)
def read_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un vehículo por su ID.
    """
    db_vehiculo = repository_vehiculo.get_vehiculo_by_id(db, vehiculo_id=vehiculo_id)
    if db_vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return db_vehiculo

@router.get("/conductor/{conductor_id}", response_model=List[Vehiculo])
def read_vehiculos_by_conductor(
    conductor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de vehículos de un conductor específico.
    """
    return repository_vehiculo.get_vehiculos_by_conductor(db, conductor_id=conductor_id)

@router.put("/{vehiculo_id}", response_model=Vehiculo)
def update_existing_vehiculo(
    vehiculo_id: int, 
    vehiculo_update: VehiculoUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un vehículo. Solo el conductor propietario puede actualizarlo.
    """
    if current_user.rol != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden actualizar sus vehículos.")
        
    return repository_vehiculo.update_vehiculo(db, vehiculo_id, vehiculo_update, current_user.id)

@router.delete("/{vehiculo_id}", status_code=200)
def delete_existing_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un vehículo. Solo el conductor propietario puede eliminarlo.
    """
    if current_user.rol != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden eliminar sus vehículos.")

    return repository_vehiculo.delete_vehiculo(db, vehiculo_id, current_user.id)


@router.post("/{vehiculo_id}/imagen", response_model=Vehiculo)
async def upload_vehiculo_imagen(
    vehiculo_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sube una imagen para un vehículo. La imagen se optimiza y convierte a WebP.
    Conductores solo pueden subir imágenes de sus propios vehículos.
    Operadores pueden subir imágenes de cualquier vehículo.
    """
    # Verificar extensión del archivo
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Leer contenido del archivo
    content = await file.read()

    # Verificar tamaño
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Verificar que el vehículo existe
    db_vehiculo = repository_vehiculo.get_vehiculo_by_id(db, vehiculo_id)
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # Verificar permisos
    is_operador = current_user.rol == "operador"
    is_owner = db_vehiculo.conductor_id == current_user.id

    if not is_operador and not is_owner:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para actualizar este vehículo"
        )

    try:
        # Optimizar imagen a WebP
        optimized_image = optimize_image_to_webp(content)

        # Generar nombre único
        filename = f"{uuid.uuid4()}.webp"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Eliminar imagen anterior si existe
        if db_vehiculo.imagen:
            old_path = os.path.join(UPLOAD_DIR, os.path.basename(db_vehiculo.imagen))
            if os.path.exists(old_path):
                os.remove(old_path)

        # Guardar nueva imagen
        with open(file_path, "wb") as f:
            f.write(optimized_image)

        # Actualizar base de datos
        imagen_url = f"/uploads/vehiculos/{filename}"

        if is_operador:
            return repository_vehiculo.update_vehiculo_imagen_operador(db, vehiculo_id, imagen_url)
        else:
            return repository_vehiculo.update_vehiculo_imagen(db, vehiculo_id, imagen_url, current_user.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")
