from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.database import Base

from app.config import settings

from app.api.v1.endpoints import router as api_router
from app.routes.agente import router as agente_router
from app.routes.chat import router as chat_router

from app.routes.predicciones import (
    router as predicciones_router
)

from app.models import models


Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend del Sistema de Gestión de Turnos Inteligente - Caso UPS Sede Cuenca",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)

app.include_router(
    agente_router
)

app.include_router(
    chat_router
)

app.include_router(
    predicciones_router
)

@app.get("/", tags=["Healthcheck"])
def health_check():
    return {
        "status": "healthy",
        "architecture": "Clean Layers",
        "cloud_ready": True
    }