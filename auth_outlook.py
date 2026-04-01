from outlook_utils import cargar_credenciales
from O365 import Account, FileSystemTokenBackend

def auth():
    creds = cargar_credenciales()
    if not creds or creds.get("client_id") == "REEMPLAZA_CON_TU_CLIENT_ID":
        print("❌ Reemplaza tu client_id en outlook_credentials.json primero.")
        return

    credentials = (creds.get("client_id"), creds.get("client_secret", ""))
    token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
    account = Account(credentials, auth_flow='authorization', token_backend=token_backend, tenant_id=creds.get("tenant_id", "common"))
    
    if account.is_authenticated:
        print("✅ Ya estás autenticado. El archivo o365_token.txt es válido.")
    else:
        print("🔐 Iniciando autenticación.")
        print("1. Haz clic en el enlace que aparecerá a continuación.")
        print("2. Inicia sesión con tu cuenta de Microsoft/Outlook.")
        print("3. Te redigirá a una página en blanco o a otra URL. Copia esa URL completa de la barra de direcciones.")
        print("4. Pégala aquí en la consola y presiona Enter.")
        # Se requieren los mismos scopes que en outlook_utils.py para ser válidos
        account.authenticate(scopes=['Calendars.ReadWrite'])
        print("✅ Autenticación completada. El archivo o365_token.txt ha sido creado.")

if __name__ == '__main__':
    auth()
