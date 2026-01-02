from pydantic import BaseModel
from typing import Optional

class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class RolCreate(RolBase):
    pass

class RolUpdate(RolBase):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class Rol(RolBase):
    id: int

    class Config:
        from_attributes = True
