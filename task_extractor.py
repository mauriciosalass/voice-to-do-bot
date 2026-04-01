import re
from config import VERBOS_ACCION, FECHA_REGEX, HORA_REGEX

def extraer_tarea(texto):
    texto = texto.lower()

    # Fecha y hora
    fecha_match = re.search(FECHA_REGEX, texto)
    hora_match = re.search(HORA_REGEX, texto)

    fecha = fecha_match.group() if fecha_match else None
    hora = hora_match.group() if hora_match else None

    # Verbo de acción
    accion = next((verbo for verbo in VERBOS_ACCION if verbo in texto), None)

    # Extraer el contenido (lo que sigue después del verbo)
    contenido = ""
    if accion:
        partes = texto.split(accion, 1)
        if len(partes) > 1:
            contenido = partes[1]
            # Quitamos fecha y hora del contenido
            if fecha:
                contenido = contenido.replace(fecha, '')
            if hora:
                contenido = contenido.replace(hora, '')
            contenido = contenido.replace(" para ", " ").replace(" a las ", " ")
            # Limpiar espacios extra y capitalizar
            contenido = re.sub(r'\s+', ' ', contenido).strip(",.:- ").capitalize()
            # Si quedó vacío o con muy pocos caracteres, intentamos usar el verbo + lo que quedó original
            if len(contenido) < 2:
                 contenido = accion.capitalize()

    return {
        "accion": accion,
        "titulo": contenido if contenido else None,
        "fecha": fecha,
        "hora": hora
    }
