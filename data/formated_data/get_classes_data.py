import json
from datetime import datetime
from collections import defaultdict

def modify_event(event):
    # Cambiar "FUNCIONAL 360" a "FUNCIONAL"
    if event['activity'] == "FUNCIONAL 360":
        event['activity'] = "FUNCIONAL"
    if event['studio'] == "Sala Fitness":
        event['studio'] = "FUNCIONAL"
    # Cambiar "Studio Ciclo" a "Studio 1"
    if event['studio'] == "Studio Ciclo":
        event['studio'] = "Studio 1"
    return event

def group_events_by_weekday_hour(events):
    grouped = defaultdict(list)
    for event in events:
        modified_event = modify_event(event)
        # Extraer el día de la semana (como número) y la hora de 'startedAt'
        start_time = datetime.strptime(modified_event['startedAt'], "%Y-%m-%dT%H:%M:%S")
        weekday = start_time.isoweekday()  # 1 para lunes, 7 para domingo
        hour = start_time.strftime("%H")
        key = f"{weekday}_{hour}"
        grouped[key].append(modified_event)
    return grouped

def transform_json(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Asegurarse de que data es una lista
    if isinstance(data, dict):
        data = list(data.values())

    # Agrupar los eventos por día de la semana (número) y hora
    grouped_events = group_events_by_weekday_hour(data)

    # Añadir cada grupo al archivo JSON correspondiente
    for key, events in grouped_events.items():
        filename = f"{key}.json"
        file_path = "data/formated_data/zones/" + filename
        
        try:
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = {}  # Cambiado de [] a {} ya que parece que quieres un diccionario
        
        # Añadir eventos al diccionario existente
        existing_data["classes"] = events
        
        # Guardar los eventos directamente en el archivo JSON
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)
            
        print(f"Eventos añadidos al archivo: {filename}")

if __name__ == "__main__":
    transform_json("data/excel/clases_total.json")