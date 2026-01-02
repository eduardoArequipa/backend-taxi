from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from models.enums import EstadoViaje
from .common import Point
from geoalchemy2.elements import WKBElement
from shapely.wkb import loads

class SolicitudBase(BaseModel):
    direccion_texto: str
    precio_ofrecido: float

class SolicitudCreate(SolicitudBase):
    origen_lat: float
    origen_lon: float
    destino_lat: float
    destino_lon: float

class Solicitud(SolicitudBase):
    id: int
    pasajero_id: int
    estado: EstadoViaje
    fecha_creacion: Optional[datetime] = None
    origen_geom: Optional[Point] = None
    destino_geom: Optional[Point] = None

    class Config:
        from_attributes = True

    @field_validator('origen_geom', 'destino_geom', mode='before')
    @classmethod
    def transform_geometry(cls, v):
        if isinstance(v, WKBElement):
            p = loads(bytes(v.data))
            return {"type": "Point", "coordinates": [p.x, p.y]}
        return v
