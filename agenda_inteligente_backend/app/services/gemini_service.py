from google import genai
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def interpretar_mensaje(texto: str):

    prompt = f"""
Eres un asistente médico.

IMPORTANTE:
La intención SOLO puede ser:

- agendar_cita
- cancelar_cita
- consultar_citas
- reagendar_cita

Mensaje:
{texto}

Responde únicamente JSON válido:

{{
  "intencion":"",
  "especialidad":"",
  "fecha":"",
  "hora":""
}}
"""

    respuesta = None

    for intento in range(3):

        try:

            respuesta = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            break

        except Exception as e:

            print(
                f"ERROR GEMINI intento {intento + 1}:",
                e
            )

            time.sleep(3)

    if not respuesta:

        raise Exception(
            "Gemini no respondió después de varios intentos"
        )

    contenido = (
        respuesta.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    print("RESPUESTA GEMINI:")
    print(contenido)

    return json.loads(contenido)