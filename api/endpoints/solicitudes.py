from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from repository import solicitud as repository_solicitud
from schemas.solicitud import Solicitud, SolicitudCreate
from schemas.usuario import User
from api.dependencies import get_current_user, get_current_pasajero, require_roles
from core.websockets import manager
from models.enums import RolUsuario

router = APIRouter()

@router.post("/", response_model=Solicitud)
async def create_solicitud(
    solicitud: SolicitudCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pasajero)  # Solo pasajeros pueden crear solicitudes
):
    """
    Crea una nueva solicitud de viaje. Solo disponible para pasajeros.
    """
    db_solicitud = repository_solicitud.create_solicitud(db=db, solicitud=solicitud, pasajero_id=current_user.id)
    solicitud_data = Solicitud.model_validate(db_solicitud)
    await manager.broadcast(f"New solicitud: {solicitud_data.model_dump_json()}")
    return db_solicitud

@router.get("/", response_model=List[Solicitud])
def read_solicitudes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RolUsuario.operador, RolUsuario.conductor]))
):
    """
    Obtiene todas las solicitudes. Solo disponible para operadores y conductores.
    """
    solicitudes = repository_solicitud.get_solicitudes(db, skip=skip, limit=limit)
    return solicitudes

@router.get("/me", response_model=List[Solicitud])
def read_solicitudes_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las solicitudes de viaje para el usuario actual (pasajero).
    """
    solicitudes = repository_solicitud.get_solicitudes_by_pasajero(db, pasajero_id=current_user.id)
    return solicitudes
