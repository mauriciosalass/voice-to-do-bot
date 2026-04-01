from __future__ import print_function
import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permiso para gestionar eventos
SCOPES = ['https://www.googleapis.com/auth/calendar']


def crear_evento_google(tarea):
    creds = None

    # Intenta cargar token existente
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si no hay token válido, iniciar login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar token para próximos usos
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Conectarse a la API de Google Calendar
    service = build('calendar', 'v3', credentials=creds)

    # Extraer la información validada por Inteligencia Artificial
    fecha_str = tarea.get('fecha') or datetime.date.today().isoformat()
    hora_str = tarea.get('hora') or "12:00"
    accion = tarea.get('accion') or "Tarea delegada al asistente de voz"
    titulo = tarea.get('titulo') or "Recordatorio de Voice-To-Do"

    # Construir datetime en formato ISO (provisto directamente por la IA)
    inicio = f"{fecha_str}T{hora_str}:00"
    
    # Otorgar una duración de 1 hora al evento para Google Calendar
    try:
        dt_inicio = datetime.datetime.fromisoformat(inicio)
        fin = (dt_inicio + datetime.timedelta(hours=1)).isoformat()
    except Exception:
        fin = inicio

    evento = {
        'summary': titulo,
        'description': f"Acción: {accion}",
        'start': {'dateTime': inicio, 'timeZone': 'America/Santiago'},
        'end': {'dateTime': fin, 'timeZone': 'America/Santiago'},
    }

    # Crear el evento
    event = service.events().insert(calendarId='primary', body=evento).execute()
    print("📅 Evento creado exitosamente:")
    print(event.get('htmlLink'))
