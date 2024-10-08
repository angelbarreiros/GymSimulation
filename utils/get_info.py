import json
import math
from classes.Map import Area, Boundary, SpawnPoint
AFORO_PATH = 'data/aforo.json'    
AFORO_ZONAS_PATH = 'data/aforo_zonas.json'
AFORO_CLASES_PATH = 'data/clases.json'




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
        name = zona['zona']
        aforo_zonas[name] = {'aforo': zona['aforo'],'ocupancy': zona['oc.prom']}
        
        
    result = {}
    for k, v in aforo_zonas.items():
        result[k]={'targetCapacity':v['ocupancy'],'totalCapacity':v['aforo']}
    result['NOFUNCIONAL']={'targetCapacity':10,'totalCapacity':10}
    return result

def extract_clases(aforo_clases_path):
    with open(aforo_clases_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    aforo_clases = {}
    for clase in data:
        aforo_clases[clase['studio']] = {
            'aforo': clase['bookedAttendees'],
        }
    
    return aforo_clases

def get_data(floor):
    with open('data/Zonas.json', 'r') as file:
        data = json.load(file)

    floorZones = data[floor]["Zonas"]
    floorWalls = data[floor]["Paredes"]
    floorSpawns = data[floor]["Spawns"]

    
    hora, entrada, salida = extract_aforo(AFORO_PATH)

    aforo_zonas = extract_aforo_zonas(AFORO_ZONAS_PATH)

    aforo_clases = extract_clases(AFORO_CLASES_PATH)


    
    
     
    
    areas = []
    paredes = []
    spawns = []

    for zone in floorZones:
        
        familia = zone["Familia"]
        name = zone["Nombre"]
        points = zone["Cordenadas"]
        numberOfSameZones = sum(1 for obj in floorZones if obj['Familia'] ==familia )
        
        try:
            totalCapacity = aforo_zonas.get(familia).get('totalCapacity')
            targetCapacity =  aforo_zonas.get(familia).get('targetCapacity')
            area = Area(name, points, targetCapacity, math.floor(totalCapacity/numberOfSameZones))  
            areas.append(area)
        except Exception:
            area = Area(name, points, 100, 100) 
            areas.append(area)
        
        

        
        
    
    for pared in floorWalls: 
        pared = Boundary(pared)
        paredes.append(pared)

    npersons = entrada-salida

    for spawn in floorSpawns:
        spawn = SpawnPoint(spawn["Nombre"], spawn["Cordenadas"])
        spawns.append(spawn)

    return npersons, areas, paredes, spawns