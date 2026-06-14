from app.database import SessionLocal
from app.models.models import DisponibilidadMedico

db = SessionLocal()

for d in db.query(DisponibilidadMedico).all():
    print(
        f"medico={d.medico_id}",
        f"dia={d.dia_semana}",
        f"inicio={d.hora_inicio}",
        f"fin={d.hora_fin}",
        f"activo={d.activo}"
    )
