from sqlalchemy.orm import Session, joinedload
from models.viaje import Viaje
from models.solicitud import Solicitud
from models.enums import EstadoViaje
from schemas.viaje import ViajeCreate, ViajeStatusUpdate
from fastapi import HTTPException
from datetime import datetime

def get_viaje_by_id(db: Session, viaje_id: int):
    return db.query(Viaje).filter(Viaje.id == viaje_id).first()

def create_viaje(db: Session, viaje: ViajeCreate, conductor_id: int):
    solicitud = db.query(Solicitud).filter(Solicitud.id == viaje.solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud not found")

    # Check if a viaje already exists for this solicitud
    existing_viaje = db.query(Viaje).filter(Viaje.solicitud_id == viaje.solicitud_id).first()
    if existing_viaje:
        raise HTTPException(status_code=400, detail="A trip for this request already exists")

    # Cambiar el estado de la solicitud a 'en_curso'
    solicitud.estado = EstadoViaje.en_curso

    db_viaje = Viaje(
        solicitud_id=viaje.solicitud_id,
        conductor_id=conductor_id,
        vehiculo_id=viaje.vehiculo_id,
        precio_final=viaje.precio_final,
    )
    db.add(db_viaje)
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def get_viajes_by_conductor(db: Session, conductor_id: int):
    """Obtiene todos los viajes de un conductor con la información de la solicitud"""
    return db.query(Viaje).options(joinedload(Viaje.solicitud)).filter(Viaje.conductor_id == conductor_id).all()

def iniciar_viaje(db: Session, viaje_id: int, conductor_id: int):
    """Marca un viaje como iniciado"""
    db_viaje = get_viaje_by_id(db, viaje_id)
    if not db_viaje:
        raise HTTPException(status_code=404, detail="Viaje not found")

    if db_viaje.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this viaje")

    if db_viaje.hora_inicio:
        raise HTTPException(status_code=400, detail="Trip already started")

    db_viaje.hora_inicio = datetime.utcnow()
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def finalizar_viaje(db: Session, viaje_id: int, conductor_id: int):
    """Marca un viaje como finalizado"""
    db_viaje = get_viaje_by_id(db, viaje_id)
    if not db_viaje:
        raise HTTPException(status_code=404, detail="Viaje not found")

    if db_viaje.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this viaje")

    if not db_viaje.hora_inicio:
        raise HTTPException(status_code=400, detail="Trip must be started before it can be finished")

    if db_viaje.completado:
        raise HTTPException(status_code=400, detail="Trip already completed")

    db_viaje.hora_fin = datetime.utcnow()
    db_viaje.completado = True

    # Actualizar el estado de la solicitud a 'finalizado'
    solicitud = db.query(Solicitud).filter(Solicitud.id == db_viaje.solicitud_id).first()
    if solicitud:
        solicitud.estado = EstadoViaje.finalizado

    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def update_viaje_status(db: Session, viaje_id: int, status_update: ViajeStatusUpdate, conductor_id: int):
    db_viaje = get_viaje_by_id(db, viaje_id)
    if not db_viaje:
        raise HTTPException(status_code=404, detail="Viaje not found")

    if db_viaje.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this viaje")

    # Assuming 'estado' is part of ViajeStatusUpdate schema
    db_viaje.estado = status_update.estado
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

def marcar_como_pagado(db: Session, viaje_id: int, conductor_id: int):
    """Marca un viaje como pagado (pago en efectivo)"""
    db_viaje = get_viaje_by_id(db, viaje_id)
    if not db_viaje:
        raise HTTPException(status_code=404, detail="Viaje not found")

    if db_viaje.conductor_id != conductor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this viaje")

    if not db_viaje.completado:
        raise HTTPException(status_code=400, detail="Trip must be completed before marking as paid")

    if db_viaje.pagado:
        raise HTTPException(status_code=400, detail="Trip already marked as paid")

    db_viaje.pagado = True
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

