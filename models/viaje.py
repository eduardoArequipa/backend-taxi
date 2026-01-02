from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.database import Base
from models.enums import EstadoViaje

class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True)
    conductor_id = Column(Integer, ForeignKey("usuarios.id"))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    precio_final = Column(Float(10, 2))
    estado = Column(Enum(EstadoViaje), default=EstadoViaje.pendiente)
    hora_inicio = Column(DateTime)
    hora_fin = Column(DateTime)
    completado = Column(Boolean, default=False)
    pagado = Column(Boolean, default=False)

    solicitud = relationship("Solicitud", back_populates="viaje")
    conductor = relationship("Usuario", back_populates="viajes_conductor", foreign_keys=[conductor_id])
    vehiculo = relationship("Vehiculo", back_populates="viajes")
