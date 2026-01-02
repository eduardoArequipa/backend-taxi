from sqlalchemy.orm import Session
from models.rol import Rol
from schemas.rol import RolCreate, RolUpdate
from fastapi import HTTPException

def create_rol(db: Session, rol: RolCreate):
    """
    Crea un nuevo rol.
    """
    db_rol = Rol(**rol.model_dump())
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

def get_rol_by_id(db: Session, rol_id: int):
    """
    Obtiene un rol por su ID.
    """
    return db.query(Rol).filter(Rol.id == rol_id).first()

def get_rol_by_nombre(db: Session, nombre: str):
    """
    Obtiene un rol por su nombre.
    """
    return db.query(Rol).filter(Rol.nombre == nombre).first()

def get_all_roles(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los roles.
    """
    return db.query(Rol).offset(skip).limit(limit).all()

def update_rol(db: Session, rol_id: int, rol_update: RolUpdate):
    """
    Actualiza la información de un rol.
    """
    db_rol = db.query(Rol).filter(Rol.id == rol_id).first()

    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    update_data = rol_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rol, key, value)
    
    db.commit()
    db.refresh(db_rol)
    return db_rol

def delete_rol(db: Session, rol_id: int):
    """
    Elimina un rol.
    """
    db_rol = db.query(Rol).filter(Rol.id == rol_id).first()

    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    db.delete(db_rol)
    db.commit()
    return {"detail": "Rol eliminado"}
