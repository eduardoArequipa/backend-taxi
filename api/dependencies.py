from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from repository import usuario as repository_usuario
from schemas.usuario import User
from models.enums import RolUsuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = repository_usuario.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


def require_roles(allowed_roles: List[RolUsuario]):
    """
    Dependencia que verifica si el usuario tiene uno de los roles permitidos.
    Uso: Depends(require_roles([RolUsuario.operador, RolUsuario.conductor]))
    """
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para realizar esta acción. Roles requeridos: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def get_current_pasajero(current_user = Depends(get_current_user)):
    """Verifica que el usuario sea un pasajero"""
    if current_user.rol != RolUsuario.pasajero:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pasajeros pueden realizar esta acción"
        )
    return current_user


def get_current_conductor(current_user = Depends(get_current_user)):
    """Verifica que el usuario sea un conductor"""
    if current_user.rol != RolUsuario.conductor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los conductores pueden realizar esta acción"
        )
    return current_user


def get_current_operador(current_user = Depends(get_current_user)):
    """Verifica que el usuario sea un operador"""
    if current_user.rol != RolUsuario.operador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los operadores pueden realizar esta acción"
        )
    return current_user
