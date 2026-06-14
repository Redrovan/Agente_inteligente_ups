from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.prediccion_service import (
    predecir_tiempo_espera
)

router = APIRouter(
    prefix="/api/v1/predicciones",
    tags=["Predicciones IA"]
)


@router.get(
    "/espera/{cita_id}"
)
def obtener_prediccion(
    cita_id: int,
    db: Session = Depends(get_db)
):

    resultado = (
        predecir_tiempo_espera(
            db,
            cita_id
        )
    )

    if not resultado:

        return {
            "error":
            "Cita no encontrada"
        }

    return resultado