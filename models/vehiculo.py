from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    conductor_id = Column(Integer, ForeignKey("usuarios.id"))
    marca = Column(String(50))
    modelo = Column(String(50))
    placa = Column(String(20), unique=True, nullable=False)
    color = Column(String(20))
    anio = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    imagen = Column(String(255), nullable=True)  # Ruta de la imagen

    conductor = relationship("Usuario", back_populates="vehiculos")
    viajes = relationship("Viaje", back_populates="vehiculo")
