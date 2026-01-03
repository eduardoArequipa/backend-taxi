from sqlalchemy.orm import Session
from models.tarifa import Tarifa
from schemas.tarifa import TarifaCreate, TarifaUpdate
from fastapi import HTTPException
from sqlalchemy.sql import func
from datetime import datetime

def create_tarifa(db: Session, tarifa: TarifaCreate):
    """
    Crea una nueva tarifa. Si ya existe una tarifa activa, la desactiva.
    """
    # Desactivar todas las tarifas activas existentes
    if tarifa.activo:
        db.query(Tarifa).filter(Tarifa.activo == True).update({"activo": False})
    
    db_tarifa = Tarifa(**tarifa.model_dump())
    db_tarifa.fecha_actualizacion = datetime.utcnow()
    db.add(db_tarifa)
    db.commit()
    db.refresh(db_tarifa)
    return db_tarifa

def get_tarifa_activa(db: Session):
    """
    Obtiene la tarifa activa.
    """
    return db.query(Tarifa).filter(Tarifa.activo == True).first()

def get_tarifas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las tarifas.
    """
    return db.query(Tarifa).order_by(Tarifa.fecha_actualizacion.desc()).offset(skip).limit(limit).all()

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
    
    # Si se va a activar esta tarifa, desactivar las demás primero
    if update_data.get("activo") is True:
        db.query(Tarifa).filter(Tarifa.id != tarifa_id).update({"activo": False})

    for key, value in update_data.items():
        setattr(db_tarifa, key, value)
    
    db_tarifa.fecha_actualizacion = datetime.utcnow()
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
    db_tarifa.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_tarifa)
    return db_tarifa