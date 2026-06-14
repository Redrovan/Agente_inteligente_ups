from datetime import timedelta

from app.models.models import (
    Cita,
    Notificacion,
    DisponibilidadMedico
)

from app.services.disponibilidad_service import (
    obtener_horarios_disponibles
)


def reagendar_automaticamente(
    db,
    medico_id,
    disponibilidad
):

    dias = {
        "MONDAY": 0,
        "TUESDAY": 1,
        "WEDNESDAY": 2,
        "THURSDAY": 3,
        "FRIDAY": 4,
        "SATURDAY": 5,
        "SUNDAY": 6
    }

    dia_desactivado = dias.get(
        disponibilidad.dia_semana
    )

    if dia_desactivado is None:
        return 0

    citas = (
        db.query(Cita)
        .filter(
            Cita.medico_id == medico_id,
            Cita.estado.in_(
                ["programada", "reagendada"]
            )
        )
        .all()
    )

    total = 0

    for cita in citas:

        if (
            cita.fecha_hora.weekday()
            != dia_desactivado
        ):
            continue

        nueva_fecha = (
            cita.fecha_hora.date()
            + timedelta(days=1)
        )

        horarios = []

        for _ in range(14):

            horarios = (
                obtener_horarios_disponibles(
                    db,
                    medico_id,
                    nueva_fecha
                )
            )

            if horarios:
                break

            nueva_fecha += timedelta(days=1)

        if not horarios:
            continue

        nueva_hora = horarios[0]

        hora = int(
            nueva_hora.split(":")[0]
        )

        minuto = int(
            nueva_hora.split(":")[1]
        )

        cita.fecha_hora = (
            cita.fecha_hora.replace(
                year=nueva_fecha.year,
                month=nueva_fecha.month,
                day=nueva_fecha.day,
                hour=hora,
                minute=minuto
            )
        )

        cita.estado = "reagendada"

        notificacion = Notificacion(
            paciente_id=cita.paciente_id,
            mensaje=(
                f"Su cita fue reagendada automáticamente "
                f"para {cita.fecha_hora}"
            )
        )

        db.add(notificacion)

        total += 1

    db.commit()

    return total