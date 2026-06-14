from datetime import (
    datetime,
    timedelta
)

from sqlalchemy.orm import Session

from app.models.models import (
    DisponibilidadMedico,
    Cita
)


def obtener_horarios_disponibles(
    db: Session,
    medico_id: int,
    fecha
):

    dias = {
        0: "MONDAY",
        1: "TUESDAY",
        2: "WEDNESDAY",
        3: "THURSDAY",
        4: "FRIDAY",
        5: "SATURDAY",
        6: "SUNDAY"
    }

    dia_semana = dias[
        fecha.weekday()
    ]

    disponibilidad = (
        db.query(
            DisponibilidadMedico
        )
        .filter(
            DisponibilidadMedico.medico_id
            == medico_id,

            DisponibilidadMedico.dia_semana
            == dia_semana,

            DisponibilidadMedico.activo
            == True
        )
        .first()
    )

    if not disponibilidad:
        return []

    hora_actual = datetime.combine(
        fecha,
        disponibilidad.hora_inicio
    )

    hora_fin = datetime.combine(
        fecha,
        disponibilidad.hora_fin
    )

    horarios = []

    while hora_actual < hora_fin:

        ocupado = (
            db.query(Cita)
            .filter(
                Cita.medico_id == medico_id,
                Cita.estado != "cancelada",
                Cita.fecha_hora == hora_actual
            )
            .first()
        )

        if not ocupado:

            horarios.append(
                hora_actual.strftime("%H:%M")
            )

        hora_actual += timedelta(
            minutes=
            disponibilidad.duracion_cita
        )

    return horarios