from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en las variables de entorno")

# Configuracion de seguridad para contraseñas
# Forzamos schemes=["bcrypt"] y una configuración que evite errores con versiones modernas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fix para compatibilidad con bcrypt moderno y passlib antiguo
# Esto evita el error "AttributeError: module 'bcrypt' has no attribute '__about__'"
import logging
logging.getLogger("passlib").setLevel(logging.ERROR)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña en texto plano contra su hash.
    Bcrypt tiene un límite de 72 caracteres, por lo que truncamos para evitar errores.
    """
    try:
        return pwd_context.verify(plain_password[:72], hashed_password)
    except Exception as e:
        print(f"Error verificando password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Genera un hash a partir de una contraseña en texto plano.
    """
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
