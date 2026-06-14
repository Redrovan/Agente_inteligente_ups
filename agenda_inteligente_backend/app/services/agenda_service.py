from datetime import (
    datetime,
    timedelta,
    date
)

from sqlalchemy.orm import Session

from app.models.models import (
    DisponibilidadMedico,
    Cita
)


def generar_agenda_semanal(
    db: Session,
    medico_id: int
):

    agenda = {}

    configuraciones = (
        db.query(DisponibilidadMedico)
        .filter(
            DisponibilidadMedico.medico_id == medico_id,
            DisponibilidadMedico.activo == True
        )
        .all()
    )

    for config in configuraciones:

        slots = []

        hora_actual = datetime.combine(
            date.today(),
            config.hora_inicio
        )

        hora_fin = datetime.combine(
            date.today(),
            config.hora_fin
        )

        while hora_actual < hora_fin:

            hora_str = hora_actual.strftime("%H:%M")

            cita = (
                db.query(Cita)
                .filter(
                    Cita.medico_id == medico_id
                )
                .filter(
                    Cita.fecha_hora.strftime("%H:%M")
                    if False else True
                )
                .all()
            )

            ocupado = False

            citas = (
                db.query(Cita)
                .filter(
                    Cita.medico_id == medico_id,
                    Cita.estado != "cancelada"
                )
                .all()
            )

            for c in citas:

                if (
                    c.fecha_hora.strftime("%H:%M")
                    == hora_str
                ):
                    ocupado = True
                    break

            slots.append({
                "hora": hora_str,
                "estado":
                    "ocupado"
                    if ocupado
                    else "libre"
            })

            hora_actual += timedelta(
                minutes=config.duracion_cita
            )

        agenda[config.dia_semana] = slots

    return agenda