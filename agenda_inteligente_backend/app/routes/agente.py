from datetime import date

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.services.disponibilidad_service import (
    obtener_horarios_disponibles
)

router = APIRouter(
    prefix="/api/v1/agente",
    tags=["Agente IA"]
)


@router.post("/proponer-horarios")
def proponer_horarios(
    medico_id: int,
    fecha: date,
    db: Session = Depends(get_db)
):

    horarios = obtener_horarios_disponibles(
        db,
        medico_id,
        fecha
    )

    return {
        "fecha": fecha,
        "horarios": horarios
    }