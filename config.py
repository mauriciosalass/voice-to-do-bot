# config.py

# Lista unificada de verbos de acción comunes en tareas
VERBOS_ACCION = [
    "revisar", "enviar", "hacer", "llamar", "estudiar", "leer", "escribir",
    "comprar", "terminar", "organizar", "presentar", "preparar", "resolver",
    "repasar"
]

# Regex para detectar hora (ej: 10, 10:30, 17 hrs, 5 pm, 10 am, 16:00)
HORA_REGEX = r"\b(?:[0-2]?[0-9][:h][0-5][0-9]\s*(?:am|pm|a\.m\.|p\.m\.|hrs|h)?|[0-2]?[0-9]\s*(?:am|pm|a\.m\.|p\.m\.|hrs|h|horas|hora))\b"

# Regex para detectar fechas como "lunes", "mañana", "24 de octubre"
FECHA_REGEX = r"\b(hoy|mañana|lunes|martes|miércoles|jueves|viernes|sábado|domingo|\d{1,2}\s+de\s+[a-z]+)\b"
