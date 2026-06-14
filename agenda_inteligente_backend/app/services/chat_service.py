from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import (
    SesionChat,
    Cita
)


# =====================================
# SESIONES CHAT
# =====================================

def obtener_sesion(
    db: Session,
    telefono: str
):

    return (
        db.query(SesionChat)
        .filter(
            SesionChat.telefono == telefono
        )
        .first()
    )


def guardar_sesion(
    db: Session,
    telefono: str,
    estado: str,
    especialidad: str = None,
    medico_id: int = None,
    fecha_seleccionada: str = None,
    horarios: list = None
):

    sesion = obtener_sesion(
        db,
        telefono
    )

    if not sesion:

        sesion = SesionChat(
            telefono=telefono,
            estado=estado
        )

        db.add(sesion)

    sesion.estado = estado
    sesion.especialidad = especialidad
    sesion.medico_id = medico_id
    sesion.fecha_seleccionada = fecha_seleccionada

    if horarios:
        sesion.horarios_ofrecidos = ",".join(horarios)

    db.commit()

    db.refresh(sesion)

    return sesion

def eliminar_sesion(
    db: Session,
    telefono: str
):

    sesion = obtener_sesion(
        db,
        telefono
    )

    if sesion:

        db.delete(sesion)

        db.commit()


# =====================================
# CITAS
# =====================================

def obtener_citas_paciente(
    db: Session,
    paciente_id: int
):

    return (
        db.query(Cita)
        .filter(
            Cita.paciente_id == paciente_id,
            or_(
                Cita.estado == "programada",
                Cita.estado == "reagendada"
            )
        )
        .order_by(
            Cita.fecha_hora
        )
        .all()
    )


def cancelar_cita(
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

    cita.estado = "cancelada"

    db.commit()

    db.refresh(cita)

    return cita


def obtener_cita_por_id(
    db: Session,
    cita_id: int
):

    return (
        db.query(Cita)
        .filter(
            Cita.id == cita_id
        )
        .first()
    )


def reagendar_cita(
    db: Session,
    cita_id: int,
    nueva_fecha_hora
):

    cita = obtener_cita_por_id(
        db,
        cita_id
    )

    if not cita:
        return None

    cita.fecha_hora = nueva_fecha_hora
    cita.estado = "reagendada"

    db.commit()

    db.refresh(cita)

    return cita


def listar_mis_citas(
    db: Session,
    paciente_id: int
):

    return (
        db.query(Cita)
        .filter(
            Cita.paciente_id == paciente_id,
            Cita.estado != "cancelada"
        )
        .order_by(
            Cita.fecha_hora
        )
        .all()
    )


def obtener_historial_citas(
    db: Session,
    paciente_id: int
):

    return (
        db.query(Cita)
        .filter(
            Cita.paciente_id == paciente_id
        )
        .order_by(
            Cita.fecha_hora.desc()
        )
        .all()
    )