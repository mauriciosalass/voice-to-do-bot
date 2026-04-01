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

    # Determinar fecha y hora del evento
    fecha = tarea['fecha'] or "mañana"
    hora = tarea['hora'] or "12:00"
    accion = tarea['accion'] or "hacer"
    titulo = tarea['titulo'] or "tarea"

    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    hoy = datetime.date.today()

    # Traducir fechas relativas
    if fecha in dias_semana:
        hoy_dia = hoy.weekday()
        target_dia = dias_semana.index(fecha)
        delta = (target_dia - hoy_dia + 7) % 7
        fecha_evento = hoy + datetime.timedelta(days=delta)
    elif fecha == "mañana":
        fecha_evento = hoy + datetime.timedelta(days=1)
    else:
        fecha_evento = hoy

    # Procesar hora
    try:
        hora = hora.lower().replace("am", "").replace("pm", "").replace("hrs", "").replace("h", ":")
        partes = hora.strip().split(":")
        hora_str = f"{int(partes[0]):02}:{int(partes[1]) if len(partes) > 1 else 0:02}"
    except:
        hora_str = "12:00"

    # Construir datetime en formato ISO
    inicio = f"{fecha_evento}T{hora_str}:00"
    fin = f"{fecha_evento}T{hora_str}:00"

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
