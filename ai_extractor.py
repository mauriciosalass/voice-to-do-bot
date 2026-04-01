import json
import datetime

def analizar_texto_con_ia(texto, openai_client):
    try:
        hoy = datetime.datetime.now()
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        hoy_str = f"{dias_semana[hoy.weekday()]} {hoy.strftime('%Y-%m-%d')}"
        
        prompt = f"""
Hoy es {hoy_str}, y la hora actual del servidor en tu zona horaria es {hoy.strftime('%H:%M')}.
El usuario envió un mensaje de voz pidiendo agendar un evento en su Google Calendar.

Extrae la información y devuelve estrictamente un JSON válido con esta estructura:
{{
  "es_tarea": true,
  "titulo": "Título de la tarea o evento corto y claro",
  "accion": "Descripción completa a realizar (con quién, dónde, contexto adicional).",
  "fecha": "YYYY-MM-DD",
  "hora": "HH:MM"
}}

Reglas CRITICAS de deducción:
- Calcula "fecha" (YYYY-MM-DD). Si dice "el miércoles", asume que es el miércoles de ESTA SEMANA. Si ese día ya pasó esta semana, entonces es el miércoles de la PRÓXIMA SEMANA. 
- "hora" debe usar formato 24 horas (ej. 10 pm = 22:00, 3 de la tarde = 15:00). Si no especifica hora explícita, usa 12:00.
- Si el mensaje no parece una tarea que se pueda agendar, entonces devuelve {{"es_tarea": false}}.

Mensaje del usuario transcrito: "{texto}"
"""
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "Eres un asistente extractor de Tareas de Calendario. Solo generas un objeto JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        contenido = response.choices[0].message.content
        datos = json.loads(contenido)
        return datos
    except Exception as e:
        print(f"Error analizando con IA: {e}")
        return None
