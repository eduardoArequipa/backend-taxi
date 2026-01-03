from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.tarifa import Tarifa, TarifaCreate, TarifaUpdate
from repository import tarifa as repository_tarifa
from api.dependencies import get_current_user
from models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=List[Tarifa])
def read_all_tarifas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene todas las tarifas. Solo el operador puede listar todas.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede ver todas las tarifas.")
    
    return repository_tarifa.get_tarifas(db, skip=skip, limit=limit)

@router.post("/", response_model=Tarifa, status_code=status.HTTP_201_CREATED)
def create_new_tarifa(
    tarifa: TarifaCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva tarifa. Solo el operador puede crear tarifas.
    Al crear una nueva tarifa, todas las tarifas anteriores se desactivan automáticamente.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede crear tarifas.")
    
    return repository_tarifa.create_tarifa(db=db, tarifa=tarifa)

@router.get("/activa", response_model=Tarifa)
def read_tarifa_activa(db: Session = Depends(get_db)):
    """
    Obtiene la tarifa activa actualmente.
    """
    db_tarifa = repository_tarifa.get_tarifa_activa(db)
    if db_tarifa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay tarifa activa configurada.")
    return db_tarifa

@router.get("/{tarifa_id}", response_model=Tarifa)
def read_tarifa_by_id(tarifa_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una tarifa por su ID.
    """
    db_tarifa = repository_tarifa.get_tarifa_by_id(db, tarifa_id=tarifa_id)
    if db_tarifa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarifa no encontrada.")
    return db_tarifa

@router.put("/{tarifa_id}", response_model=Tarifa)
def update_existing_tarifa(
    tarifa_id: int,
    tarifa_update: TarifaUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una tarifa existente. Solo el operador puede actualizar tarifas.
    Si se activa una tarifa, las demás se desactivan.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede actualizar tarifas.")
    
    return repository_tarifa.update_tarifa(db, tarifa_id, tarifa_update)

@router.delete("/{tarifa_id}", response_model=Tarifa) # Usamos DELETE para desactivar, no borrar físicamente
def deactivate_existing_tarifa(
    tarifa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desactiva una tarifa existente. Solo el operador puede desactivar tarifas.
    Las tarifas no se eliminan, solo se marcan como inactivas.
    """
    if current_user.rol != "operador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el operador puede desactivar tarifas.")
    
    return repository_tarifa.deactivate_tarifa(db, tarifa_id)
