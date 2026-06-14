import re
from datetime import date, timedelta
import os
from fastapi import Request, APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.disponibilidad_service import obtener_horarios_disponibles
from app.services.paciente_service import obtener_paciente_por_telefono

from app.services.chat_service import (
    obtener_sesion,
    eliminar_sesion,
    obtener_citas_paciente,
    cancelar_cita,
    reagendar_cita,
    obtener_cita_por_id,
    listar_mis_citas,
    obtener_historial_citas
)

from app.services.cita_service import (
    guardar_sesion,
    registrar_cita_desde_chat,
    construir_fecha_hora
)

from app.services.nlp_service import extraer_hora

router = APIRouter(
    prefix="/api/v1",
    tags=["Agente IA Demo"]
)


@router.get("/webhook")
async def verificar_webhook(request: Request):
    """
    Sincroniza y valida el webhook con Meta Developers usando el token del .env
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    token_esperado = os.getenv("VERIFY_TOKEN", "agenda_ups_2026")

    if mode == "subscribe" and token == token_esperado:
        return int(challenge)

    return {"error": "token inválido"}


@router.post("/chat")
def chat(
    mensaje: dict,
    db: Session = Depends(get_db)
):
    texto = mensaje["mensaje"].strip()
    telefono = mensaje.get("telefono", "demo")

    paciente = obtener_paciente_por_telefono(db, telefono)

    if not paciente:
        return {
            "respuesta": "Paciente no registrado en el sistema del Centro Médico."
        }

    texto_lower = texto.lower()
    sesion = obtener_sesion(db, telefono)

    # =====================================
    # REAGENDAR - NUEVO HORARIO
    # =====================================
    if sesion and sesion.estado == "esperando_nuevo_horario":
        horarios = sesion.horarios_ofrecidos.split(",")
        hora_detectada = extraer_hora(texto)

        if hora_detectada and hora_detectada in horarios:
            nueva_fecha_hora = construir_fecha_hora(
                sesion.fecha_objetivo,
                hora_detectada
            )

            cita = reagendar_cita(db, int(sesion.cita_id), nueva_fecha_hora)
            eliminar_sesion(db, telefono)

            return {
                "respuesta": f"¡Éxito! Tu cita con ID {cita.id} ha sido reagendada correctamente para las {hora_detectada}."
            }

        return {
            "respuesta": "Por favor, seleccione uno de los horarios ofrecidos indicando la hora exacta.",
            "horarios": horarios
        }

    # =====================================
    # REAGENDAR - SELECCIONAR CITA
    # =====================================
    if (
        sesion
        and sesion.estado == "esperando_cita_reagendar"
        and texto.isdigit()
    ):
        cita = obtener_cita_por_id(db, int(texto))

        if not cita:
            return {
                "respuesta": "La cita con el ID ingresado no existe. Intente nuevamente."
            }

        fecha_consulta = date.today()
        horarios = []

        for _ in range(7):
            horarios = obtener_horarios_disponibles(db, cita.medico_id, fecha_consulta)
            if horarios:
                break
            fecha_consulta += timedelta(days=1)

        sesion.estado = "esperando_nuevo_horario"
        sesion.cita_id = cita.id
        sesion.fecha_objetivo = str(fecha_consulta)
        sesion.horarios_ofrecidos = ",".join(horarios)

        db.commit()

        return {
            "respuesta": f"Buscando disponibilidad para el {fecha_consulta}. Seleccione el nuevo horario deseado:",
            "horarios": horarios
        }

    # =====================================
    # CANCELAR CITA POR ID
    # =====================================
    if texto.isdigit():
        cita = cancelar_cita(db, int(texto))

        if cita:
            eliminar_sesion(db, telefono)
            return {
                "respuesta": f"Confirmado: La cita con ID {cita.id} ha sido cancelada correctamente."
            }

    # =====================================
    # REAGENDAR CITA (MENÚ INICIAL)
    # =====================================
    if "reagendar" in texto_lower:
        eliminar_sesion(db, telefono)
        citas = obtener_citas_paciente(db, paciente.id)

        if not citas:
            return {
                "respuesta": "No encontramos citas activas programadas en tu cuenta para reagendar."
            }

        listado = []
        for cita in citas:
            listado.append({
                "id": cita.id,
                "fecha": str(cita.fecha_hora)
            })

        guardar_sesion(db, telefono, [])
        sesion = obtener_sesion(db, telefono)
        sesion.estado = "esperando_cita_reagendar"
        db.commit()

        return {
            "respuesta": "Responda con el número ID de la cita que desea reagendar:",
            "citas": listado
        }

    # =====================================
    # SOLICITUD DE CANCELACION (MENÚ INICIAL)
    # =====================================
    if "cancelar" in texto_lower:
        eliminar_sesion(db, telefono)
        citas = obtener_citas_paciente(db, paciente.id)

        if not citas:
            return {
                "respuesta": "No registras citas activas programadas que se puedan cancelar."
            }

        listado = []
        for cita in citas:
            listado.append({
                "id": cita.id,
                "fecha": str(cita.fecha_hora),
                "estado": cita.estado
            })

        return {
            "respuesta": "Responda únicamente con el número ID de la cita que desea cancelar:",
            "citas": listado
        }

    # =====================================
    # SELECCION DE HORARIO (AGENDAMIENTO NUEVO)
    # =====================================
    if sesion and sesion.estado == "esperando_horario":
        horarios = sesion.horarios_ofrecidos.split(",")
        hora_detectada = extraer_hora(texto)

        if hora_detectada and hora_detectada in horarios:
            cita = registrar_cita_desde_chat(
                db=db,
                fecha=str(date.today()),
                hora=hora_detectada,
                medico_id=1,
                paciente_id=paciente.id
            )

            if not cita:
                return {
                    "respuesta": "Lo siento, ese horario acaba de ser reservado por otro paciente. Intente con otro:",
                    "horarios": horarios
                }

            eliminar_sesion(db, telefono)

            return {
                "respuesta": f"¡Cita confirmada con éxito! Te esperamos a las {hora_detectada}.",
                "cita_id": cita.id
            }

        return {
            "respuesta": "El horario ingresado no es válido. Seleccione uno de los que tenemos disponibles:",
            "horarios": horarios
        }

    # =====================================
    # MIS CITAS
    # =====================================
    if "mis citas" in texto_lower:
        citas = listar_mis_citas(db, paciente.id)

        if not citas:
            return {
                "respuesta": "Actualmente no tienes citas agendadas próximamente."
            }

        listado = []
        for cita in citas:
            listado.append({
                "id": cita.id,
                "fecha": str(cita.fecha_hora),
                "estado": cita.estado
            })

        return {
            "respuesta": "Estas son tus citas actualmente vigentes:",
            "citas": listado
        }

    # =====================================
    # HISTORIAL
    # =====================================
    if "historial" in texto_lower:
        citas = obtener_historial_citas(db, paciente.id)

        if not citas:
            return {
                "respuesta": "No posees un registro antiguo de citas finalizadas."
            }

        listado = []
        for cita in citas:
            listado.append({
                "id": cita.id,
                "fecha": str(cita.fecha_hora),
                "estado": cita.estado
            })

        return {
            "respuesta": "Este es el desglose histórico de tus consultas atendidas:",
            "citas": listado
        }

    # =====================================
    # NUEVA CITA
    # =====================================
    if "cita" in texto_lower:
        horarios = []
        fecha_consulta = date.today()

        for _ in range(7):
            horarios = obtener_horarios_disponibles(db, 1, fecha_consulta)
            if horarios:
                break
            fecha_consulta += timedelta(days=1)

        horarios = horarios[:5]

        if not horarios:
            return {
                "respuesta": "No se encontraron turnos médicos disponibles para esta semana."
            }

        guardar_sesion(db, telefono, horarios)

        return {
            "fecha": str(fecha_consulta),
            "horarios": horarios,
            "respuesta": f"Turnos disponibles para el {fecha_consulta}. Por favor, responda con la hora elegida:"
        }

    return {
        "respuesta": "Hola, soy el asistente del Centro Médico UPS. Puedo ayudarte a: 'agendar una cita', 'cancelar', 'reagendar' o revisar 'mis citas'. ¿Qué deseas hacer?"
    }


@router.post("/webhook")
async def recibir_whatsapp(
    payload: dict,
    db: Session = Depends(get_db)
):
    # Importación interna para evitar cualquier atadura circular residual
    from app.services.whatsapp_service import enviar_mensaje

    print("\n\n========== WEBHOOK ENTRANTE ==========")
    print(payload)
    print("================================")
    print("MENSAJE REAL RECIBIDO")
    print(payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"])
    print("================================")
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

        respuesta_meta = enviar_mensaje(
            telefono_usr,
            texto_final
        )

        print("RESPUESTA META:")
        print(respuesta_meta)

        return {"status": "ok"}

    except Exception as e:
        print("🚨 ERROR EN PROCESAMIENTO WEBHOOK:", e)
        return {"status": "error"}