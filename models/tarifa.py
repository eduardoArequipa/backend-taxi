from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database.database import Base
from sqlalchemy.sql import func

class Tarifa(Base):
    __tablename__ = "tarifas"

    id = Column(Integer, primary_key=True, index=True)
    tarifa_base = Column(Float(10, 2), default=5.00)
    costo_por_km = Column(Float(10, 2), default=3.50)
    moneda = Column(String(10), default="BOB")
    activo = Column(Boolean, default=True)
    fecha_actualizacion = Column(DateTime, default=func.now())
