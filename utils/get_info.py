import json
from classes.Map import Area, Boundary, SpawnPoint

# Mapping of current zone names to standardized zone names
zone_mapping = {
    "PP": "PP",
    "PG": "PG",
    "SAUNA": "SAUNA",
    "BAÑO VAPOR": "VAPOR",
    "PP EXT": "PP",  # Assuming PP EXT is part of PP
    "SOLARIUM": "DESCANSO",  # Assuming SOLARIUM is part of DESCANSO
    "DESCANSO": "DESCANSO",
    "CARDIO": "CARDIO",
    "CIRCUIT": "CIRCUIT",
    "CORE": "CORE",
    "FUNCIONAL": "FUNCIONAL",
    "ISOTÓNICO": "ISOTONICO",
    "PESO_LIBRE": "PESO LIBRE",
    "X-TRAINING": "XTRAINING"
}

# List of all standardized zones
all_zones = {
    "PP", 
    "PG",
    "SAUNA",
    "VAPOR",
    "DESCANSO",
    "HIDROMASAJE",
    "VESTUARIO FEMENINO",
    "VESTUARIO MASCULINO",
    "XTRAINING",
    "KIDS",
    "LUDOTECA",
    "CARDIO",
    "CIRCUIT",
    "CORE", 
    "FUNCIONAL", 
    "PESO LIBRE",
    "ISOTONICO",
}

def extract_aforo(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    hora = data['hora']
    entrada = data['entrada']
    salida = data['salida']
    
    return hora, entrada, salida

def extract_aforo_zonas(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    aforo_zonas = {}
    for zona in data:
        original_name = zona['zona']
        standardized_name = zone_mapping.get(original_name, original_name)
        if standardized_name in aforo_zonas:
            aforo_zonas[standardized_name]['aforo'] += zona['aforo']
        else:
            aforo_zonas[standardized_name] = {'aforo': zona['aforo']}
    
    return [{'zona': k, 'aforo': v['aforo']} for k, v in aforo_zonas.items()]

def extract_clases(aforo_clases_path):
    with open(aforo_clases_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    aforo_clases = {}
    for clase in data:
        aforo_clases[clase['studio']] = {
            'aforo': clase['bookedAttendees'],
        }
    
    return aforo_clases

def get_data():
    with open('data/Zonas.json', 'r') as file:
        data = json.load(file)

    planta2_zones = data["Planta2"]["Zonas"]
    planta2_paredes = data["Planta2"]["Paredes"]
    planta2_spawns = data["Planta2"]["Spawns"]

    aforo_path = 'data/aforo.json'
    aforo_zonas_path = 'data/aforo_zonas.json'
    aforo_clases_path = 'data/clases.json'
    hora, entrada, salida = extract_aforo(aforo_path)
    aforo_zonas = extract_aforo_zonas(aforo_zonas_path)
    aforo_clases = extract_clases(aforo_clases_path)
    aforo_dict = {zona['zona']: zona['aforo'] for zona in aforo_zonas}

    print(f"aforo_dict: {aforo_dict}")
    areas = []
    paredes = []
    spawns = []
    for zone in planta2_zones:
        id = zone["Nombre"]
        points = zone["Cordenadas"]
        aforo = aforo_dict.get(id, None)
        
        if aforo is not None:
            print(f"Found aforo {aforo} for zone '{id}'")
            area = Area(id, points, aforo)
        else:
            print(f"Warning: No aforo found for zone '{id}'. Using 0 value.")
            area = Area(id, points, 0)  
        areas.append(area)
    
    for pared in planta2_paredes: 
        pared = Boundary(pared)
        paredes.append(pared)

    npersons = entrada -salida

    for spawn in planta2_spawns:
        spawn = SpawnPoint(spawn["Nombre"], spawn["Cordenadas"])
        spawns.append(spawn)

    return npersons, areas, paredes, spawns

if __name__ == "__main__":
    aforo_path = 'code/engañiza/data2/aforo.json'
    aforo_zonas_path = 'code/engañiza/data2/aforo_zonas.json'
    aforo_clases_path = 'code/engañiza/data2/clases.json'
    
    hora, entrada, salida = extract_aforo(aforo_path)
    aforo_zonas = extract_aforo_zonas(aforo_zonas_path)
    aforo_clases = extract_clases(aforo_clases_path)
    
    print(f"Hora: {hora}, Entrada: {entrada}, Salida: {salida}")
    print("Aforo por zonas:")
    for zona in aforo_zonas:
        print(f"Zona: {zona['zona']}, Aforo: {zona['aforo']}")
    print("Aforo por clases:")
    for clase, info in aforo_clases.items():
        print(f"Clase: {clase}, Aforo: {info['aforo']}")
