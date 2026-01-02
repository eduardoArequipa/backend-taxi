from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from database.database import Base
import enum

class RolUsuario(str, enum.Enum):
    pasajero = "pasajero"
    conductor = "conductor"
    operador = "operador"

class EstadoViaje(str, enum.Enum):
    pendiente = "pendiente"
    en_curso = "en_curso"
    finalizado = "finalizado"
    cancelado = "cancelado"

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


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    conductor_id = Column(Integer, ForeignKey("usuarios.id"))
    marca = Column(String(50))
    modelo = Column(String(50))
    placa = Column(String(20), unique=True, nullable=False)
    color = Column(String(20))

    conductor = relationship("Usuario", back_populates="vehiculos")
    viajes = relationship("Viaje", back_populates="vehiculo")


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    pasajero_id = Column(Integer, ForeignKey("usuarios.id"))
    origen_geom = Column(Geometry('POINT', srid=4326))
    destino_geom = Column(Geometry('POINT', srid=4326))
    direccion_texto = Column(String)
    precio_ofrecido = Column(Float(10, 2), nullable=False)
    estado = Column(Enum(EstadoViaje), default=EstadoViaje.pendiente)
    fecha_creacion = Column(DateTime)

    pasajero = relationship("Usuario", back_populates="solicitudes")
    viaje = relationship("Viaje", back_populates="solicitud")


class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True)
    conductor_id = Column(Integer, ForeignKey("usuarios.id"))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    precio_final = Column(Float(10, 2))
    hora_inicio = Column(DateTime)
    hora_fin = Column(DateTime)
    completado = Column(Boolean, default=False)

    solicitud = relationship("Solicitud", back_populates="viaje")
    conductor = relationship("Usuario", back_populates="viajes_conductor", foreign_keys=[conductor_id])
    vehiculo = relationship("Vehiculo", back_populates="viajes")
