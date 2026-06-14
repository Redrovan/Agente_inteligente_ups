from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import (
    Cita,
    SesionChat
)


def registrar_cita_desde_chat(
    db: Session,
    fecha: str,
    hora: str,
    medico_id: int,
    paciente_id: int
):

    fecha_hora = datetime.strptime(
        f"{fecha} {hora}",
        "%Y-%m-%d %H:%M"
    )

    # =====================================
    # VALIDAR QUE EL HORARIO NO ESTÉ OCUPADO
    # =====================================

    cita_existente = (
        db.query(Cita)
        .filter(
            Cita.medico_id == medico_id,
            Cita.fecha_hora == fecha_hora,
            Cita.estado != "cancelada"
        )
        .first()
    )

    if cita_existente:
        return None

    # =====================================
    # CREAR CITA
    # =====================================

    cita = Cita(
        medico_id=medico_id,
        paciente_id=paciente_id,
        fecha_hora=fecha_hora,
        tipo_servicio="control",
        estado="programada"
    )

    db.add(cita)

    db.commit()

    db.refresh(cita)

    return cita


def guardar_sesion(
    db: Session,
    telefono: str,
    horarios: list[str]
):

    sesion_anterior = (
        db.query(SesionChat)
        .filter(
            SesionChat.telefono == telefono
        )
        .first()
    )

    if sesion_anterior:

        db.delete(sesion_anterior)

        db.commit()

    sesion = SesionChat(
        telefono=telefono,
        estado="esperando_horario",
        horarios_ofrecidos=",".join(horarios)
    )

    db.add(sesion)

    db.commit()

    db.refresh(sesion)

    return sesion


def construir_fecha_hora(
    fecha: str,
    hora: str
):

    return datetime.strptime(
        f"{fecha} {hora}",
        "%Y-%m-%d %H:%M"
    )

