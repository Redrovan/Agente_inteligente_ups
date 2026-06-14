from sqlalchemy.orm import Session

from app.models.models import Cita

from app.models.models import Cita


def obtener_demanda(
    db: Session
):

    total_citas = (
        db.query(Cita)
        .filter(
            Cita.estado.in_(
                ["programada", "reagendada"]
            )
        )
        .count()
    )

    if total_citas < 5:
        nivel = "BAJA"

    elif total_citas < 15:
        nivel = "MEDIA"

    else:
        nivel = "ALTA"

    return {
        "total_citas": total_citas,
        "nivel_demanda": nivel
    }


def predecir_tiempo_espera(
    db: Session,
    cita_id: int
):

    cita = (
        db.query(Cita)
        .filter(
            Cita.id == cita_id
        )
        .first()
    )

    if not cita:
        return None

    citas_anteriores = (
        db.query(Cita)
        .filter(
            Cita.medico_id == cita.medico_id,
            Cita.fecha_hora < cita.fecha_hora,
            Cita.estado.in_(
                ["programada", "reagendada"]
            )
        )
        .all()
    )

    pacientes_antes = len(
        citas_anteriores
    )

    duracion_promedio = 20

    tiempo_espera = (
        pacientes_antes *
        duracion_promedio
    )

    return {
        "cita_id": cita.id,
        "fecha": cita.fecha_hora,
        "pacientes_antes": pacientes_antes,
        "duracion_promedio": duracion_promedio,
        "tiempo_espera": tiempo_espera
    }