import os
import json
import datetime
from O365 import Account, FileSystemTokenBackend

CREDENTIALS_FILE = 'outlook_credentials.json'

def cargar_credenciales():
    if not os.path.exists(CREDENTIALS_FILE):
        plantilla = {
            "client_id": "REEMPLAZA_CON_TU_CLIENT_ID",
            "client_secret": "REEMPLAZA_CON_TU_CLIENT_SECRET",
            "tenant_id": "common"
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(plantilla, f, indent=4)
        print(f"⚠️ Se ha creado '{CREDENTIALS_FILE}'.")
        print("Por favor, pon tus credenciales ahí antes de continuar.")
        return None
    
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def crear_evento_outlook(tarea):
    creds = cargar_credenciales()
    if not creds:
        return False
        
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    tenant_id = creds.get("tenant_id", "common")

    if client_id == "REEMPLAZA_CON_TU_CLIENT_ID":
        print("⚠️ Aún no has puesto tu Client ID en outlook_credentials.json")
        return False

    credentials = (client_id, client_secret)

    # FileSystemTokenBackend guarda la sesión activa para no loguearte cada vez.
    token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
    
    # scope Calendars.ReadWrite nos permite crear eventos
    scopes = ['Calendars.ReadWrite']
    
    print("Conectando con Microsoft Outlook...")
    account = Account(credentials, auth_flow='authorization', token_backend=token_backend, tenant_id=tenant_id)
    
    if not account.is_authenticated:
        # Esto imprimirá un enlace en la consola. 
        # Tienes que abrirlo, aceptar los permisos y pegar el enlace resultante de vulta aquí.
        print("🔐 Iniciando autorización por primera vez...")
        account.authenticate(scopes=scopes)

    # 1. Determinar Fecha
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    hoy = datetime.date.today()
    fecha_str = tarea.get('fecha') or "mañana"
    
    if fecha_str in dias_semana:
        hoy_dia = hoy.weekday()
        target_dia = dias_semana.index(fecha_str)
        delta = (target_dia - hoy_dia + 7) % 7
        if delta == 0: delta = 7
        fecha_evento = hoy + datetime.timedelta(days=delta)
    elif fecha_str == "mañana":
        fecha_evento = hoy + datetime.timedelta(days=1)
    else:
        # Fallback a hoy si es muy compleja por ahora
        fecha_evento = hoy

    # 2. Determinar Hora
    hora_str = tarea.get('hora') or "12:00"
    try:
        es_pm = "p" in hora_str.lower()
        hora_limpia = hora_str.lower().replace("am", "").replace("pm", "").replace("hrs", "").replace("h", ":").strip()
        partes = hora_limpia.split(":")
        h = int(partes[0])
        m = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else 0
        
        if es_pm and h < 12:
            h += 12
    except:
        h, m = 12, 0

    # Crear datetime con zona horaria base (UTC o local dependiendo del sistema)
    # Lo más sano es crear uno "naive" y que la librería ponga la de defecto, o especificar timezone
    import zoneinfo
    tz = zoneinfo.ZoneInfo("America/Santiago")
    
    inicio = datetime.datetime.combine(fecha_evento, datetime.time(h, m)).replace(tzinfo=tz)
    fin = inicio + datetime.timedelta(hours=1)

    # 3. Crear el evento en el calendario principal
    try:
        schedule = account.schedule()
        calendar = schedule.get_default_calendar()
        
        new_event = calendar.new_event()
        new_event.subject = tarea.get('titulo') or "Tarea de Voz nueva"
        new_event.body = f"Acción principal: {tarea.get('accion')}"
        new_event.start = inicio
        new_event.end = fin
        
        # Guarda y manda la invitación al calendario
        new_event.save()
        print(f"📅 ¡Evento de Outlook creado exitosamente!: '{new_event.subject}' para el {inicio.strftime('%d/%m a las %H:%M')}")
        return True
    except Exception as e:
        print(f"❌ Ocurrió un error al guardar en Outlook: {e}")
        return False
