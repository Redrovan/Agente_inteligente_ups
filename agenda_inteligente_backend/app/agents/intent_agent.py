from enum import Enum


class Intent(str, Enum):
    AGENDAR = "AGENDAR"
    CANCELAR = "CANCELAR"
    CONSULTAR = "CONSULTAR"
    DESCONOCIDA = "DESCONOCIDA"


def detectar_intencion(mensaje: str) -> Intent:

    mensaje = mensaje.lower().strip()

    palabras_agendar = [
        "cita",
        "agendar",
        "reservar",
        "turno",
        "quiero una cita",
        "programar"
    ]

    palabras_cancelar = [
        "cancelar",
        "anular",
        "eliminar cita",
        "cancelar turno"
    ]

    palabras_consultar = [
        "consultar",
        "ver cita",
        "mi cita",
        "tengo cita",
        "estado"
    ]

    for palabra in palabras_agendar:
        if palabra in mensaje:
            return Intent.AGENDAR

    for palabra in palabras_cancelar:
        if palabra in mensaje:
            return Intent.CANCELAR

    for palabra in palabras_consultar:
        if palabra in mensaje:
            return Intent.CONSULTAR

    return Intent.DESCONOCIDA