from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database.database import Base
from models.enums import EstadoViaje

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
