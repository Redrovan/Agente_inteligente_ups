from dotenv import load_dotenv
import requests
import os

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")


def enviar_mensaje(numero: str, mensaje: str):
    """
    Envía un mensaje de texto plano al usuario final usando la API Cloud de WhatsApp.
    """
    url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        return response.json()
    except Exception as e:
        print(f"🚨 Error en la conexión saliente de requests hacia Meta API: {e}")
        return {"error": str(e)}


# =====================================================================
# PUENTE DE INTENCIONES CONECTADO A BASE DE DATOS (MÁQUINA DE ESTADOS)
# =====================================================================

def procesar_mensaje(mensaje: str, telefono: str = "593982544829"):
    """
    Función puente requerida por app/api/v1/endpoints.py para procesar el 
    mensaje de manera interactiva con el core del chat y PostgreSQL,
    retornando la estructura plana exacta para evitar KeyErrors.
    """
    # IMPORTACIÓN LOCAL (Lazy Import) para romper de raíz el bucle circular de python
    from app.database import SessionLocal
    from app.routes.webhook import chat

    # Creamos una sesión limpia de la Base de Datos para el procesamiento
    db = SessionLocal()
    try:
        payload_chat = {
            "mensaje": mensaje,
            "telefono": telefono
        }
        
        # Ejecutamos el flujo real de la máquina de estados del chat (agendar, consultar, etc.)
        resultado_chat = chat(payload_chat, db)
        
        # Si la respuesta del core es un diccionario válido, extraemos y aplanamos el JSON
        if isinstance(resultado_chat, dict):
            return {
                "intencion_detectada": "maquina_de_estados_ups",
                "respuesta": resultado_chat.get("respuesta", "Operación procesada.")
            }
        
        # En caso de que devuelva una cadena o formato inesperado
        return {
            "intencion_detectada": "error_formato_interno",
            "respuesta": str(resultado_chat)
        }
        
    except Exception as e:
        print(f"🚨 Error interno en función puente de whatsapp_service: {e}")
        return {
            "intencion_detectada": "excepcion_servidor",
            "respuesta": f"Lo siento, ocurrió un error interno en el servidor médico: {str(e)}"
        }
    finally:
        # Cerramos la conexión a la base de datos de manera segura para evitar fugas en el pool
        db.close()