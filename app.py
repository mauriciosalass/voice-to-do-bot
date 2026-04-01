import whisper
from task_validator import es_tarea_valida
from task_extractor import extraer_tarea
from task_storage import guardar_tarea
from calendar_utils import crear_evento_google

model = whisper.load_model("base")
result = model.transcribe("audios/probando.m4a")
texto_detectado = result["text"]

print("Texto detectado:")
print(texto_detectado)

# Validación de si es tarea o no
if es_tarea_valida(texto_detectado):
    print("✅ ¡Tarea reconocida correctamente!")
    tarea = extraer_tarea(texto_detectado)
    print("🧠 Tarea interpretada:")
    print(tarea)

    guardar_tarea(tarea)
    print("💾 Tarea guardada en 'tasks.json' correctamente.")

    # Elegir destino
    destino = input("\n¿Dónde deseas agendar esta tarea? [g] Google / [o] Outlook / [a] Ambos: ").strip().lower()

    if destino in ['g', 'a']:
        crear_evento_google(tarea)
    
    if destino in ['o', 'a']:
        from outlook_utils import crear_evento_outlook
        crear_evento_outlook(tarea)

    if destino not in ['g', 'o', 'a']:
        print("Opción no reconocida. No se agendó en ningún calendario.")

else:
    print("⚠️ No pude reconocer una tarea. Intenta usar una estructura como:")
    print("👉 'Revisar informe el lunes a las 10 de la mañana'")
