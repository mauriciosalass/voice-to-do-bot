import re
from config import VERBOS_ACCION, FECHA_REGEX, HORA_REGEX

def es_tarea_valida(texto):
    texto = texto.lower()
    hay_verbo = any(verbo in texto for verbo in VERBOS_ACCION)
    hay_fecha = bool(re.search(FECHA_REGEX, texto))
    hay_hora = bool(re.search(HORA_REGEX, texto))

    return hay_verbo and hay_fecha and hay_hora
