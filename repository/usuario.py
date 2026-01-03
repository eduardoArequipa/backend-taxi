from sqlalchemy.orm import Session
from models.usuario import Usuario
from schemas.usuario import UserCreate
from core.security import pwd_context
from models.enums import RolUsuario

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def get_users_by_rol(db: Session, rol: RolUsuario, skip: int = 0, limit: int = 100):
    return db.query(Usuario).filter(Usuario.rol == rol).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password[:72])
    db_user = Usuario(
        email=user.email,
        nombre=user.nombre,
        telefono=user.telefono,
        rol=user.rol,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: Usuario, user_update: dict):
    for field, value in user_update.items():
        if value is not None:
            setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_password(db: Session, db_user: Usuario, new_password: str):
    hashed_password = pwd_context.hash(new_password[:72])
    db_user.password = hashed_password
    db.commit()
    return True

