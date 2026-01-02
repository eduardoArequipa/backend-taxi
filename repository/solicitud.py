from sqlalchemy.orm import Session
from models.solicitud import Solicitud
from schemas.solicitud import SolicitudCreate
from models.usuario import Usuario

def create_solicitud(db: Session, solicitud: SolicitudCreate, pasajero_id: int):
    # Crear las geometrías POINT a partir de las coordenadas
    origen_geom = f'POINT({solicitud.origen_lon} {solicitud.origen_lat})'
    destino_geom = f'POINT({solicitud.destino_lon} {solicitud.destino_lat})'

    # Crear la solicitud solo con los campos que existen en el modelo
    db_solicitud = Solicitud(
        direccion_texto=solicitud.direccion_texto,
        precio_ofrecido=solicitud.precio_ofrecido,
        pasajero_id=pasajero_id,
        origen_geom=origen_geom,
        destino_geom=destino_geom
    )
    db.add(db_solicitud)
    db.commit()
    db.refresh(db_solicitud)
    return db_solicitud

def get_solicitudes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Solicitud).offset(skip).limit(limit).all()

def get_solicitud_by_id(db: Session, solicitud_id: int):
    return db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()

def get_solicitudes_by_pasajero(db: Session, pasajero_id: int, skip: int = 0, limit: int = 100):
    return db.query(Solicitud).filter(Solicitud.pasajero_id == pasajero_id).offset(skip).limit(limit).all()