import re
from config import FECHA_REGEX, HORA_REGEX

def es_tarea_valida(texto):
    texto = texto.lower()
    hay_fecha = bool(re.search(FECHA_REGEX, texto))
    hay_hora = bool(re.search(HORA_REGEX, texto))

    return hay_fecha and hay_hora
