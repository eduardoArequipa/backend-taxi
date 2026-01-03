from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TarifaBase(BaseModel):
    tarifa_base: float
    costo_por_km: float
    costo_por_minuto: Optional[float] = 0.0
    moneda: Optional[str] = "BOB"
    activo: Optional[bool] = True

class TarifaCreate(TarifaBase):
    pass

class TarifaUpdate(TarifaBase):
    tarifa_base: Optional[float] = None
    costo_por_km: Optional[float] = None
    costo_por_minuto: Optional[float] = None
    moneda: Optional[str] = None
    activo: Optional[bool] = None

class Tarifa(TarifaBase):
    id: int
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
