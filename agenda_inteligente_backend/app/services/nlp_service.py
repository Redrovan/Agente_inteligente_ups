import re


def extraer_hora(texto: str):

    texto = texto.lower().strip()

    patrones = [
        r"(\d{1,2}):(\d{2})",
        r"(\d{1,2})\s*am",
        r"a las (\d{1,2})",
        r"la de las (\d{1,2})",
        r"(\d{1,2})"
    ]

    for patron in patrones:

        match = re.search(
            patron,
            texto
        )

        if match:

            hora = int(match.group(1))

            minutos = "00"

            if len(match.groups()) > 1:
                minutos = match.group(2)

            return f"{hora:02d}:{minutos}"

    return None