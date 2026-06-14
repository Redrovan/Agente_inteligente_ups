from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    Medico,
    Paciente,
    Cita
)


def obtener_dashboard(db: Session):

    total_medicos = (
        db.query(func.count(Medico.id))
        .scalar()
    )

    total_pacientes = (
        db.query(func.count(Paciente.id))
        .scalar()
    )

    total_citas = (
        db.query(func.count(Cita.id))
        .scalar()
    )

    citas_programadas = (
        db.query(func.count(Cita.id))
        .filter(Cita.estado == "programada")
        .scalar()
    )

    citas_canceladas = (
        db.query(func.count(Cita.id))
        .filter(Cita.estado == "cancelada")
        .scalar()
    )

    citas_reagendadas = (
        db.query(func.count(Cita.id))
        .filter(Cita.estado == "reagendada")
        .scalar()
    )

    hora_pico = (
        db.query(
            func.to_char(
                Cita.fecha_hora,
                'HH24:MI'
            ).label("hora"),
            func.count(Cita.id).label("total")
        )
        .filter(
            Cita.estado != "cancelada"
        )
        .group_by("hora")
        .order_by(
            func.count(Cita.id).desc()
        )
        .first()
    )

    return {
        "total_medicos": total_medicos,
        "total_pacientes": total_pacientes,
        "total_citas": total_citas,
        "citas_programadas": citas_programadas,
        "citas_canceladas": citas_canceladas,
        "citas_reagendadas": citas_reagendadas,
        "hora_pico": hora_pico.hora if hora_pico else None
    }