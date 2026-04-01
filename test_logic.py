import sys
from task_validator import es_tarea_valida
from task_extractor import extraer_tarea
from calendar_utils import crear_evento_google

def test_frase(texto_detectado):
    print(f"--- Prueba de Frase ---\nTexto: '{texto_detectado}'")
    
    # Validación de si es tarea o no
    if es_tarea_valida(texto_detectado):
        print("✅ ¡Tarea reconocida correctamente!")
        tarea = extraer_tarea(texto_detectado)
        print("🧠 Tarea interpretada:")
        print(tarea)
        print("-----------------------\n")
    else:
        print("⚠️ No pude reconocer una tarea (falta verbo, fecha u hora).")
        print("-----------------------\n")

if __name__ == '__main__':
    frases_prueba = [
        "necesito preparar el informe para mañana a las 10 am",
        "llamar a Juan el martes a las 15:30 hrs",
        "comprar los boletos hoy a las 5 pm",
        "revisar el auto el 24 de octubre a las 14:00"
    ]
    
    for frase in frases_prueba:
        test_frase(frase)
