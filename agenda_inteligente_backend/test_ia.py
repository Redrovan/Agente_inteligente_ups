from app.services.gemini_service import interpretar_mensaje

datos = interpretar_mensaje(
    "Necesito una cita para ginecología mañana a las 10"
)

print(datos)
print(datos["especialidad"])