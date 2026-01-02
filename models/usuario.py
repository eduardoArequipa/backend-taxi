from sqlalchemy import Column, Integer, String, Boolean, Enum
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from database.database import Base
from models.enums import RolUsuario

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    telefono = Column(String(20))
    rol = Column(Enum(RolUsuario), nullable=False)
    ubicacion = Column(Geometry('POINT', srid=4326))
    activo = Column(Boolean, default=True)

    vehiculos = relationship("Vehiculo", back_populates="conductor")
    solicitudes = relationship("Solicitud", back_populates="pasajero")

    viajes_conductor = relationship("Viaje", back_populates="conductor", foreign_keys="[Viaje.conductor_id]")
