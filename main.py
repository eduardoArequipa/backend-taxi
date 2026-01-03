from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.database import engine, Base
from api.endpoints import users, auth, solicitudes, tarifas, vehiculos, roles, viajes, websockets
import os
from dotenv import load_dotenv

load_dotenv()

# Crear directorio de uploads si no existe
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Estas líneas son para desarrollo y reinician la base de datos en cada arranque.
# En producción, esto debería ser manejado por Alembic o una estrategia de migración.
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Empresa Taxi API", version="1.0.0")

# Configuración de CORS
# En desarrollo, permitir todos los orígenes. En producción, especificar los dominios permitidos.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = [
        "https://api.trialsur.cloud",
        # Agrega aquí los dominios de producción
    ]
else:
    # En desarrollo, permitir orígenes específicos
    origins = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "http://192.168.100.58:8081",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(solicitudes.router, prefix="/solicitudes", tags=["solicitudes"])
app.include_router(vehiculos.router, prefix="/vehiculos", tags=["vehiculos"])
app.include_router(tarifas.router, prefix="/tarifas", tags=["tarifas"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(viajes.router, prefix="/viajes", tags=["viajes"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

# Servir archivos estáticos (imágenes de vehículos)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")