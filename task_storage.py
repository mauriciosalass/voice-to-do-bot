import json
import os

TASKS_FILE = "tasks.json"

def guardar_tarea(tarea):
    tareas = []

    # Cargar tareas existentes
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            try:
                tareas = json.load(f)
            except json.JSONDecodeError:
                tareas = []

    # Agregar nueva tarea
    tareas.append(tarea)

    # Guardar todas las tareas
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=2, ensure_ascii=False)
