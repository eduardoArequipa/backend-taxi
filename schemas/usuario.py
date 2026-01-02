from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from models.enums import RolUsuario
from .common import Point
from geoalchemy2.elements import WKBElement
from shapely.wkb import loads

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    rol: RolUsuario

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if len(v) > 72:
            raise ValueError('La contraseña no puede tener más de 72 caracteres (límite de bcrypt)')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class User(UserBase):
    id: int
    activo: bool
    ubicacion: Optional[Point] = None

    class Config:
        from_attributes = True

    @field_validator('ubicacion', mode='before')
    @classmethod
    def transform_ubicacion(cls, v):
        if isinstance(v, WKBElement):
            p = loads(bytes(v.data))
            return {"type": "Point", "coordinates": [p.x, p.y]}
        return v
