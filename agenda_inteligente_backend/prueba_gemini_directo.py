from app.services.gemini_service import interpretar_mensaje

try:
    resultado = interpretar_mensaje(
        "Necesito una cita para ginecologia mañana"
    )

    print(resultado)

except Exception as e:
    print("ERROR:", e)
