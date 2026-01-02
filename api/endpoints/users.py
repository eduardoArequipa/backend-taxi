from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from repository import usuario as repository_usuario
from schemas.usuario import User, UserCreate
from api.dependencies import get_current_user, get_current_operador
from models.enums import RolUsuario

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registro publico - solo permite crear pasajeros.
    """
    # Forzar rol pasajero para registro publico
    if user.rol != RolUsuario.pasajero:
        raise HTTPException(status_code=403, detail="Solo puedes registrarte como pasajero")

    db_user = repository_usuario.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repository_usuario.create_user(db=db, user=user)


@router.post("/conductor", response_model=User)
def create_conductor(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operador)
):
    """
    Registra un nuevo conductor. Solo operadores pueden usar este endpoint.
    """
    # Forzar rol conductor
    user_data = user.model_dump()
    user_data['rol'] = RolUsuario.conductor
    user_obj = UserCreate(**user_data)

    db_user = repository_usuario.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repository_usuario.create_user(db=db, user=user_obj)


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operador)
):
    """
    Obtiene todos los usuarios. Solo operadores.
    """
    users = repository_usuario.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/conductores", response_model=List[User])
def read_conductores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_operador)
):
    """
    Obtiene la lista de conductores. Solo operadores.
    """
    conductores = repository_usuario.get_users_by_rol(db, rol=RolUsuario.conductor, skip=skip, limit=limit)
    return conductores
