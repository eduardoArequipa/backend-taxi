from pydantic import BaseModel
from typing import Optional

class VehiculoBase(BaseModel):
    marca: str
    modelo: str
    placa: str
    color: str
    anio: Optional[int] = None

class VehiculoCreate(VehiculoBase):
    pass  # conductor_id will be taken from the authenticated user

class VehiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    placa: Optional[str] = None
    color: Optional[str] = None
    anio: Optional[int] = None
    activo: Optional[bool] = None

class Vehiculo(VehiculoBase):
    id: int
    conductor_id: int
    activo: bool = True
    imagen: Optional[str] = None

    class Config:
        from_attributes = True

