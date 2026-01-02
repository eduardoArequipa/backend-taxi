from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from repository import viaje as repository_viaje, solicitud as repository_solicitud
from schemas.viaje import Viaje, ViajeCreate, ViajeStatusUpdate
from schemas.usuario import User
from api.dependencies import get_current_user
from core.websockets import manager

router = APIRouter()

@router.post("/", response_model=Viaje)
async def create_viaje(
    viaje: ViajeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo viaje (el conductor acepta una solicitud).
    """
    db_viaje = repository_viaje.create_viaje(db=db, viaje=viaje, conductor_id=current_user.id)

    viaje_data = Viaje.model_validate(db_viaje)
    await manager.send_personal_message_by_id(
        f"Your offer was accepted!: {viaje_data.model_dump_json()}",
        db_viaje.conductor_id
    )

    return db_viaje

@router.get("/me", response_model=list[Viaje])
def get_my_viajes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los viajes del conductor autenticado.
    """
    return repository_viaje.get_viajes_by_conductor(db, conductor_id=current_user.id)

@router.patch("/{viaje_id}/iniciar", response_model=Viaje)
async def iniciar_viaje(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia un viaje (marca la hora de inicio).
    """
    db_viaje = repository_viaje.iniciar_viaje(db, viaje_id=viaje_id, conductor_id=current_user.id)

    # Notificar al pasajero
    db_solicitud = repository_solicitud.get_solicitud_by_id(db, db_viaje.solicitud_id)
    if db_solicitud:
        viaje_data = Viaje.model_validate(db_viaje)
        await manager.send_personal_message_by_id(
            f"Trip started: {viaje_data.model_dump_json()}",
            db_solicitud.pasajero_id
        )

    return db_viaje

@router.patch("/{viaje_id}/finalizar", response_model=Viaje)
async def finalizar_viaje(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Finaliza un viaje (marca la hora de fin y lo marca como completado).
    """
    db_viaje = repository_viaje.finalizar_viaje(db, viaje_id=viaje_id, conductor_id=current_user.id)

    # Notificar al pasajero
    db_solicitud = repository_solicitud.get_solicitud_by_id(db, db_viaje.solicitud_id)
    if db_solicitud:
        viaje_data = Viaje.model_validate(db_viaje)
        await manager.send_personal_message_by_id(
            f"Trip completed: {viaje_data.model_dump_json()}",
            db_solicitud.pasajero_id
        )

    return db_viaje

@router.patch("/{viaje_id}/marcar-pagado", response_model=Viaje)
async def marcar_pagado(
    viaje_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca un viaje como pagado (pago en efectivo).
    """
    db_viaje = repository_viaje.marcar_como_pagado(db, viaje_id=viaje_id, conductor_id=current_user.id)

    # Notificar al pasajero
    db_solicitud = repository_solicitud.get_solicitud_by_id(db, db_viaje.solicitud_id)
    if db_solicitud:
        viaje_data = Viaje.model_validate(db_viaje)
        await manager.send_personal_message_by_id(
            f"Payment confirmed: {viaje_data.model_dump_json()}",
            db_solicitud.pasajero_id
        )

    return db_viaje

@router.patch("/{viaje_id}/status", response_model=Viaje)
async def update_viaje_status(
    viaje_id: int,
    status_update: ViajeStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_viaje = repository_viaje.update_viaje_status(
        db, viaje_id=viaje_id, status_update=status_update, conductor_id=current_user.id
    )

    # Notify the passenger
    db_solicitud = repository_solicitud.get_solicitud_by_id(db, db_viaje.solicitud_id)
    if db_solicitud:
        viaje_data = Viaje.model_validate(db_viaje)
        await manager.send_personal_message_by_id(
            f"Trip status updated: {viaje_data.model_dump_json()}",
            db_solicitud.pasajero_id
        )

    return db_viaje
