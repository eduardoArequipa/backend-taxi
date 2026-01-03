from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database.database import Base
from sqlalchemy.sql import func

class Tarifa(Base):
    __tablename__ = "tarifas"

    id = Column(Integer, primary_key=True, index=True)
    tarifa_base = Column(Float, default=5.00)
    costo_por_km = Column(Float, default=3.50)
    costo_por_minuto = Column(Float, default=0.50) # Aseguramos que este campo exista
    moneda = Column(String(10), default="BOB")
    activo = Column(Boolean, default=True)
    fecha_actualizacion = Column(DateTime, default=func.now())