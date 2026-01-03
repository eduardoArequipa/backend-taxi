from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.enums import EstadoViaje

class ViajeBase(BaseModel):
    pass

class ViajeCreate(ViajeBase):
    solicitud_id: int
    vehiculo_id: int
    precio_final: float

class ViajeStatusUpdate(BaseModel):
    estado: EstadoViaje

from schemas.solicitud import Solicitud

class Viaje(ViajeBase):
    id: int
    solicitud_id: int
    conductor_id: int
    vehiculo_id: Optional[int] = None
    precio_final: float
    estado: EstadoViaje
    hora_inicio: Optional[datetime] = None
    hora_fin: Optional[datetime] = None
    completado: bool
    pagado: bool = False
    solicitud: Optional[Solicitud] = None

    class Config:
        from_attributes = True
