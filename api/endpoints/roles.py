from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.rol import Rol, RolCreate, RolUpdate
from repository import rol as repository_rol
from api.dependencies import get_current_user
from schemas.usuario import User # Para verificar el rol del usuario

router = APIRouter()

@router.post("/", response_model=Rol, status_code=status.HTTP_201_CREATED)
def create_new_rol(
    rol: RolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo rol. Solo el operador puede crear roles.
    """
    if current_user.rol != "operador": # Asumiendo que "operador" es el rol administrativo
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede crear roles.")
    
    db_rol = repository_rol.get_rol_by_nombre(db, nombre=rol.nombre)
    if db_rol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rol ya existe.")

    return repository_rol.create_rol(db=db, rol=rol)

@router.get("/{rol_id}", response_model=Rol)
def read_rol_by_id(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un rol por su ID.
    Solo usuarios con rol de operador pueden acceder.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver los roles.")
    
    db_rol = repository_rol.get_rol_by_id(db, rol_id=rol_id)
    if db_rol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    return db_rol

@router.get("/", response_model=List[Rol])
def read_all_roles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los roles.
    Solo usuarios con rol de operador pueden acceder.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver los roles.")
    
    roles = repository_rol.get_all_roles(db, skip=skip, limit=limit)
    return roles

@router.put("/{rol_id}", response_model=Rol)
def update_existing_rol(
    rol_id: int,
    rol_update: RolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un rol existente. Solo el operador puede actualizar roles.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede actualizar roles.")
    
    return repository_rol.update_rol(db, rol_id, rol_update)

@router.delete("/{rol_id}", status_code=status.HTTP_200_OK)
def delete_existing_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un rol existente. Solo el operador puede eliminar roles.
    Considerar la implicación de eliminar roles que están asignados a usuarios.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede eliminar roles.")
    
    return repository_rol.delete_rol(db, rol_id)
