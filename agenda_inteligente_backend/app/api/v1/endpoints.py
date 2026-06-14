from datetime import date
from datetime import timedelta
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from fastapi.responses import PlainTextResponse

from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Cita
from app.models.models import DisponibilidadMedico
from app.models.models import Medico
from app.models.models import Notificacion
from app.schemas.schemas import CancelarCitaResponse
from app.schemas.schemas import CitaCreate
from app.schemas.schemas import CitaResponse
from app.schemas.schemas import DashboardResponse
from app.schemas.schemas import DisponibilidadMedicoCreate
from app.schemas.schemas import DisponibilidadMedicoResponse
from app.schemas.schemas import DisponibilidadRequest
from app.schemas.schemas import DisponibilidadResponse
from app.schemas.schemas import MedicoResponse
from app.schemas.schemas import PrediccionDemandaResponse
from app.schemas.schemas import ReagendarCitaRequest
from app.schemas.schemas import ReagendarCitaResponse
from app.services.agenda_service import (
    generar_agenda_semanal
)
from app.services.dashboard_service import (
    obtener_dashboard
)
from app.services.disponibilidad_service import (
    obtener_horarios_disponibles
)
from app.services.prediccion_service import (
    obtener_demanda
)

from app.models.models import (
    ConfiguracionAgenda
)

from app.schemas.schemas import (
    ConfiguracionAgendaCreate
)

from app.services.reagendamiento_automatico import (
    reagendar_automaticamente
)


router = APIRouter()

# =====================================================
# TOKEN DE VERIFICACION WEBHOOK
# =====================================================

VERIFY_TOKEN = "agenda_ups_2026"


# =====================================================
# MODELO PARA PRUEBAS RAPIDAS
# =====================================================

class TestMensaje(BaseModel):
    body: str


# =====================================================
# CONFIGURACION
# =====================================================

@router.get(
    "/medicos",
    response_model=List[MedicoResponse],
    tags=["Configuración"]
)
def obtener_medicos(db: Session = Depends(get_db)):
    """
    Obtiene la lista de médicos registrados.
    """
    return db.query(Medico).all()


# =====================================================
# DISPONIBILIDAD
# =====================================================

@router.post(
    "/disponibilidad",
    response_model=DisponibilidadResponse,
    tags=["Disponibilidad"]
)
def verificar_disponibilidad(
    payload: DisponibilidadRequest,
    db: Session = Depends(get_db)
):
    """
    Obtiene los horarios disponibles de un médico
    para una fecha determinada.
    """

    horarios = obtener_horarios_disponibles(
        db=db,
        medico_id=payload.medico_id,
        fecha=payload.fecha
    )

    return {
        "medico_id": payload.medico_id,
        "fecha": payload.fecha,
        "horarios_disponibles": horarios
    }


# =====================================================
# CITAS
# =====================================================

@router.get(
    "/citas",
    response_model=List[CitaResponse],
    tags=["Citas"]
)
def listar_citas(
    db: Session = Depends(get_db)
):
    """
    Lista todas las citas registradas.
    """

    return (
        db.query(Cita)
        .order_by(Cita.fecha_hora)
        .all()
    )


@router.put(
    "/citas/{cita_id}/cancelar",
    response_model=CancelarCitaResponse,
    tags=["Citas"]
)
def cancelar_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela una cita existente.
    """

    cita = (
        db.query(Cita)
        .filter(Cita.id == cita_id)
        .first()
    )

    if not cita:

        return {
            "mensaje": "Cita no encontrada",
            "cita_id": cita_id,
            "estado": "error"
        }

    cita.estado = "cancelada"

    db.commit()

    return {
        "mensaje": "Cita cancelada correctamente",
        "cita_id": cita.id,
        "estado": cita.estado
    }


@router.put(
    "/citas/{cita_id}/reagendar",
    response_model=ReagendarCitaResponse,
    tags=["Citas"]
)
def reagendar_cita(
    cita_id: int,
    payload: ReagendarCitaRequest,
    db: Session = Depends(get_db)
):
    """
    Reagenda una cita existente.
    """

    cita = (
        db.query(Cita)
        .filter(Cita.id == cita_id)
        .first()
    )

    if not cita:

        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    conflicto = (
        db.query(Cita)
        .filter(
            Cita.medico_id == cita.medico_id,
            Cita.fecha_hora == payload.nueva_fecha_hora,
            Cita.id != cita_id,
            Cita.estado != "cancelada"
        )
        .first()
    )

    if conflicto:

        raise HTTPException(
            status_code=400,
            detail="El nuevo horario ya está ocupado"
        )

    cita.fecha_hora = payload.nueva_fecha_hora
    cita.estado = "reagendada"

    db.commit()
    db.refresh(cita)

    return {
        "mensaje": "Cita reagendada correctamente",
        "cita_id": cita.id,
        "fecha_hora": cita.fecha_hora,
        "estado": cita.estado
    }


@router.post(
    "/configuracion-agenda"
)
def crear_configuracion(
    payload: ConfiguracionAgendaCreate,
    db: Session = Depends(get_db)
):

    config = ConfiguracionAgenda(
        medico_id=payload.medico_id,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        duracion_cita=payload.duracion_cita
    )

    db.add(config)

    db.commit()

    db.refresh(config)

    return config

@router.get(
    "/configuracion-agenda"
)
def listar_configuracion(
    db: Session = Depends(get_db)
):

    return (
        db.query(
            ConfiguracionAgenda
        )
        .all()
    )

@router.post(
    "/citas",
    response_model=CitaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Citas"]
)
def agendar_cita(
    payload: CitaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva cita validando que
    el horario no esté ocupado.
    """

    cita_existente = (
        db.query(Cita)
        .filter(
            Cita.medico_id == payload.medico_id,
            Cita.fecha_hora == payload.fecha_hora,
            Cita.estado != "cancelada"
        )
        .first()
    )

    if cita_existente:

        raise HTTPException(
            status_code=400,
            detail="El horario ya se encuentra ocupado"
        )

    nueva_cita = Cita(
        medico_id=payload.medico_id,
        paciente_id=payload.paciente_id,
        fecha_hora=payload.fecha_hora,
        tipo_servicio=payload.tipo_servicio,
        estado="programada"
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)

    return nueva_cita


# =====================================================
# PRUEBA RAPIDA DEL AGENTE
# =====================================================

@router.post(
    "/test-intent",
    tags=["Pruebas"]
)
def probar_intencion(payload: TestMensaje, db: Session = Depends(get_db)):
    from app.routes.webhook import chat
    resultado = chat({"mensaje": payload.body, "telefono": "demo"}, db)
    return resultado


# =====================================================
# AGENTE INTELIGENTE - VERIFICACION WEBHOOK (GET)
# =====================================================

@router.get(
    "/webhook",
    tags=["Agente Inteligente"]
)
async def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Verificación del webhook requerida por Meta.
    """

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print(f"\n✅ Webhook verificado correctamente")
        return PlainTextResponse(content=hub_challenge)

    print(f"\n❌ Token inválido recibido: {hub_verify_token}")
    return PlainTextResponse(content="Token inválido", status_code=403)


# =====================================================
# AGENTE INTELIGENTE - RECEPCION DE MENSAJES (POST)
# =====================================================

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    tags=["Agente Inteligente"]
)
async def webhook_agente_conversacional(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Recibe mensajes desde WhatsApp Business Cloud API.
    """
    from app.services.whatsapp_service import enviar_mensaje
    from app.routes.webhook import chat

    print("\n\n========== WEBHOOK ENTRANTE ==========")
    print(payload)
    print("======================================\n\n")

    try:
        mensaje_txt = payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        telefono_usr = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        res_dict = chat({"mensaje": mensaje_txt, "telefono": telefono_usr}, db)
        texto_final = res_dict.get("respuesta", "Operación procesada.")

        if "citas" in res_dict:
            texto_final += "\n"
            for c in res_dict["citas"]:
                estado_str = f" [{c['estado']}]" if "estado" in c else ""
                texto_final += f"\n📌 *ID:* {c['id']} - 📅 *Fecha:* {c['fecha']}{estado_str}"

        if "horarios" in res_dict:
            texto_final += "\n"
            for h in res_dict["horarios"]:
                texto_final += f"\n🕒 {h}"

        respuesta_meta = enviar_mensaje(telefono_usr, texto_final)
        print("RESPUESTA META:", respuesta_meta)

        return {"status": "ok"}

    except Exception as e:
        print(f"\n🚨 ERROR EN PROCESAMIENTO WEBHOOK: {e}")
        return {"status": "error", "detalle": str(e)}


# =====================================================
# PREDICCION
# =====================================================

@router.get(
    "/predicciones/demanda",
    response_model=PrediccionDemandaResponse,
    tags=["Predicción"]
)
def predecir_demanda(
    db: Session = Depends(get_db)
):
    """
    Analiza las citas históricas y
    determina la hora de mayor demanda.
    """

    return obtener_demanda(db)


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    tags=["Dashboard"]
)
def dashboard(
    db: Session = Depends(get_db)
):
    """
    Métricas generales del sistema.
    """

    return obtener_dashboard(db)


@router.post(
    "/configuracion/disponibilidad",
    response_model=DisponibilidadMedicoResponse,
    tags=["Configuración"]
)
def crear_disponibilidad(
    payload: DisponibilidadMedicoCreate,
    db: Session = Depends(get_db)
):

    nueva = DisponibilidadMedico(
        medico_id=payload.medico_id,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        duracion_cita=payload.duracion_cita
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get(
    "/configuracion/disponibilidad",
    response_model=List[DisponibilidadMedicoResponse],
    tags=["Configuración"]
)
def listar_disponibilidad(
    db: Session = Depends(get_db)
):

    return (
        db.query(DisponibilidadMedico)
        .all()
    )


@router.put(
    "/configuracion/disponibilidad/{disponibilidad_id}",
    response_model=DisponibilidadMedicoResponse,
    tags=["Configuración"]
)
def actualizar_disponibilidad(
    disponibilidad_id: int,
    payload: DisponibilidadMedicoCreate,
    db: Session = Depends(get_db)
):

    disponibilidad = (
        db.query(DisponibilidadMedico)
        .filter(
            DisponibilidadMedico.id == disponibilidad_id
        )
        .first()
    )

    if not disponibilidad:

        raise HTTPException(
            status_code=404,
            detail="Disponibilidad no encontrada"
        )

    disponibilidad.medico_id = payload.medico_id
    disponibilidad.dia_semana = payload.dia_semana
    disponibilidad.hora_inicio = payload.hora_inicio
    disponibilidad.hora_fin = payload.hora_fin
    disponibilidad.duracion_cita = payload.duracion_cita

    db.commit()
    db.refresh(disponibilidad)

    return disponibilidad


@router.put(
    "/configuracion/disponibilidad/{disponibilidad_id}/desactivar",
    tags=["Configuración"]
)
def desactivar_disponibilidad(
    disponibilidad_id: int,
    db: Session = Depends(get_db)
):

    disponibilidad = (
        db.query(DisponibilidadMedico)
        .filter(
            DisponibilidadMedico.id == disponibilidad_id
        )
        .first()
    )

    if not disponibilidad:

        raise HTTPException(
            status_code=404,
            detail="Disponibilidad no encontrada"
        )

    disponibilidad.activo = False

    db.commit()

    total = (
        reagendar_automaticamente(
            db,
            disponibilidad.medico_id,
            disponibilidad
        )
    )

    db.refresh(disponibilidad)

    return {
        "mensaje":
        "Disponibilidad desactivada",

        "id":
        disponibilidad.id,

        "activo":
        disponibilidad.activo,

        "citas_reagendadas":
        total
    }

# =====================================================
# AGENDA SEMANAL
# =====================================================

@router.get(
    "/agenda-semanal",
    tags=["Agenda"]
)
def agenda_semanal(
    medico_id: int = 1,
    db: Session = Depends(get_db)
):

    return generar_agenda_semanal(
        db=db,
        medico_id=medico_id
    )

@router.post(
    "/reagendar-automatico/{medico_id}"
)
def ejecutar_reagendamiento(
    medico_id: int,
    db: Session = Depends(get_db)
):

    total = (
        reagendar_automaticamente(
            db,
            medico_id,
            date.today()
        )
    )

    return {
        "citas_reagendadas": total
    }

# =====================================================
# NOTIFICACIONES
# =====================================================

@router.get(
    "/notificaciones",
    tags=["Notificaciones"]
)
def listar_notificaciones(
    db: Session = Depends(get_db)
):

    return (
        db.query(Notificacion)
        .order_by(
            Notificacion.id.desc()
        )
        .all()
    )

@router.put(
    "/citas/{cita_id}/confirmar"
)
def confirmar_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):

    cita = (
        db.query(Cita)
        .filter(Cita.id == cita_id)
        .first()
    )

    if not cita:

        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    cita.estado = "confirmada"

    db.commit()

    return {
        "mensaje": "Cita confirmada"
    }

@router.get(
    "/notificaciones"
)
def listar_notificaciones(
    db: Session = Depends(get_db)
):

    return (
        db.query(Notificacion)
        .order_by(
            Notificacion.id.desc()
        )
        .all()
    )


@router.get(
    "/dashboard-ejecutivo"
)
def dashboard_ejecutivo(
    db: Session = Depends(get_db)
):

    total_citas = db.query(Cita).count()

    programadas = (
        db.query(Cita)
        .filter(Cita.estado == "programada")
        .count()
    )

    confirmadas = (
        db.query(Cita)
        .filter(Cita.estado == "confirmada")
        .count()
    )

    reagendadas = (
        db.query(Cita)
        .filter(Cita.estado == "reagendada")
        .count()
    )

    canceladas = (
        db.query(Cita)
        .filter(Cita.estado == "cancelada")
        .count()
    )

    return {
        "total_citas": total_citas,
        "programadas": programadas,
        "confirmadas": confirmadas,
        "reagendadas": reagendadas,
        "canceladas": canceladas
    }