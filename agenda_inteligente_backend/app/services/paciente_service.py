from sqlalchemy.orm import Session

from app.models.models import Paciente


def obtener_paciente_por_telefono(
    db: Session,
    telefono: str
):

    return (
        db.query(Paciente)
        .filter(
            Paciente.whatsapp_id == telefono
        )
        .first()
    )