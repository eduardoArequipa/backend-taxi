from sqlalchemy.orm import Session
from models.vehiculo import Vehiculo
from schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from fastapi import HTTPException

def create_vehiculo(db: Session, vehiculo: VehiculoCreate, conductor_id: int):
    """
    Crea un nuevo vehículo para un conductor.
    """
    db_vehiculo = Vehiculo(**vehiculo.model_dump(), conductor_id=conductor_id)
    db.add(db_vehiculo)
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def get_vehiculo_by_id(db: Session, vehiculo_id: int):
    """
    Obtiene un vehículo por su ID.
    """
    return db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

def get_all_vehiculos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los vehículos.
    """
    return db.query(Vehiculo).offset(skip).limit(limit).all()

def get_vehiculos_by_conductor(db: Session, conductor_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los vehículos de un conductor específico.
    """
    return db.query(Vehiculo).filter(Vehiculo.conductor_id == conductor_id).offset(skip).limit(limit).all()

def update_vehiculo(db: Session, vehiculo_id: int, vehiculo_update: VehiculoUpdate, conductor_id: int):
    """
    Actualiza la información de un vehículo.
    Un conductor solo puede actualizar su propio vehículo.
    """
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    if db_vehiculo.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar este vehículo")

    update_data = vehiculo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehiculo, key, value)
    
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo

def delete_vehiculo(db: Session, vehiculo_id: int, conductor_id: int):
    """
    Elimina un vehículo.
    Un conductor solo puede eliminar su propio vehículo.
    """
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if db_vehiculo.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este vehículo")

    db.delete(db_vehiculo)
    db.commit()
    return {"detail": "Vehículo eliminado"}


def update_vehiculo_imagen(db: Session, vehiculo_id: int, imagen_path: str, conductor_id: int):
    """
    Actualiza la imagen de un vehículo.
    """
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if db_vehiculo.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar este vehículo")

    db_vehiculo.imagen = imagen_path
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo


def update_vehiculo_imagen_operador(db: Session, vehiculo_id: int, imagen_path: str):
    """
    Actualiza la imagen de un vehículo (solo operadores).
    """
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    db_vehiculo.imagen = imagen_path
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo
