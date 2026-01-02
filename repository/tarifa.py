from sqlalchemy.orm import Session
from models.tarifa import Tarifa
from schemas.tarifa import TarifaCreate, TarifaUpdate
from fastapi import HTTPException
from sqlalchemy.sql import func # Import func to use func.now()

def create_tarifa(db: Session, tarifa: TarifaCreate):
    """
    Crea una nueva tarifa. Si ya existe una tarifa activa, la desactiva.
    """
    # Desactivar todas las tarifas activas existentes
    db.query(Tarifa).filter(Tarifa.activo == True).update({"activo": False})
    
    db_tarifa = Tarifa(**tarifa.model_dump())
    db.add(db_tarifa)
    db.commit()
    db.refresh(db_tarifa)
    return db_tarifa

def get_tarifa_activa(db: Session):
    """
    Obtiene la tarifa activa.
    """
    return db.query(Tarifa).filter(Tarifa.activo == True).first()

def get_tarifa_by_id(db: Session, tarifa_id: int):
    """
    Obtiene una tarifa por su ID.
    """
    return db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()

def update_tarifa(db: Session, tarifa_id: int, tarifa_update: TarifaUpdate):
    """
    Actualiza una tarifa existente.
    """
    db_tarifa = db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()
    if not db_tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")
    
    update_data = tarifa_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tarifa, key, value)
    
    # Si se activa esta tarifa, desactivar las demás
    if "activo" in update_data and update_data["activo"] == True:
        db.query(Tarifa).filter(Tarifa.id != tarifa_id, Tarifa.activo == True).update({"activo": False})

    db_tarifa.fecha_actualizacion = func.now() # Actualizar la fecha de actualización
    db.commit()
    db.refresh(db_tarifa)
    return db_tarifa

def deactivate_tarifa(db: Session, tarifa_id: int):
    """
    Desactiva una tarifa específica.
    """
    db_tarifa = db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()
    if not db_tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")
    
    db_tarifa.activo = False
    db_tarifa.fecha_actualizacion = func.now()
    db.commit()
    db.refresh(db_tarifa)
    return db_tarifa
