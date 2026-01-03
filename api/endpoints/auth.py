from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database.database import get_db
from repository import usuario as repository_usuario
from core import security
from schemas.usuario import Token, User, UserUpdate, PasswordChange
from api.dependencies import get_current_user
from models.usuario import Usuario

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = repository_usuario.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    user_update: UserUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Update current user profile.
    """
    if user_update.email and user_update.email != current_user.email:
        db_user = repository_usuario.get_user_by_email(db, email=user_update.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    return repository_usuario.update_user(db, db_user=current_user, user_update=user_update.model_dump(exclude_unset=True))

@router.post("/me/password")
def change_password_me(
    password_data: PasswordChange = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Change current user password.
    """
    if not security.verify_password(password_data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    repository_usuario.update_password(db, db_user=current_user, new_password=password_data.new_password)
    return {"message": "Contraseña actualizada exitosamente"}
