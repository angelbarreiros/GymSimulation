import json
import math
from classes.Map import Area, Boundary, SpawnPoint, Activity
from utils.get_zones_json import get_day_name
AFORO_PATH = 'data/clases_2024-08-05.json'    
#AFORO_ZONAS_PATH = 'data/aforo_zonas_7am.json'
AFORO_ZONAS_PATH = 'data/aforo-x-horas/LUNES_07.json'
AFORO_CLASES_PATH = 'data/clases_7am.json'

def extract_aforo(file_path, hour):
    hour_str = str(hour).zfill(2)  # Ensure hour is a two-digit string
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for record in data:
        if record['hora'] == hour_str:
            entrada = record['entrada']
            salida = record['salida']
            return entrada, salida
    return entrada, salida 

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
    result['NOFUNCIONAL']={'targetCapacity':0,'totalCapacity':0}
    result['VESTUARIO']={'targetCapacity':0,'totalCapacity':0}
    result['CLASE']={'targetCapacity':0,'totalCapacity':0}
    result['CLASE']={'targetCapacity':0,'totalCapacity':0}
    
    return result


def extract_clases(aforo_clases_path,zone):
    with open(aforo_clases_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for clase in data:
        if clase['studio']==zone.name:
            targetClassArea=Area(zone.name,zone.points,clase['attendingLimit'],clase['bookedAttendees'],3,zone.type,zone.machines)
            newClass = Activity(name=clase['activity'],startDate=clase['startedAt'],endDate=clase['endedAt'],Area=targetClassArea)  
            return newClass

def get_data(dia, hora):
    AFORO_PATH = f'data/entradas_{dia}.json'
    AFORO_ZONAS_PATH = f'data/aforo-x-horas/{get_day_name(dia)}_{ str(hora).zfill(2) }.json'
    entrada, salida = extract_aforo(AFORO_PATH,  str(hora).zfill(2))

    with open('data/zones.json', 'r') as file:
        data = json.load(file)
        
        all_areas = []
        all_walls = []
        all_spawns = []
        all_classes = []
        all_classes = []
        floorNum=0
        for floor in data:
            aforo_zonas = extract_aforo_zonas(AFORO_ZONAS_PATH)

            zones= data[floor]["Zones"]
            for zone in zones:
                type = zone["Type"]
                name = zone["Name"]
                points = zone["Coordinates"]
                machines = zone["Machines"]
                numberOfSameZones = sum(1 for obj in zones if obj['Type'] == type )
                try:
                    totalCapacity = aforo_zonas.get(type).get('totalCapacity')
                    targetCapacity =  aforo_zonas.get(type).get('targetCapacity')
                    area = Area(name, points, math.floor(totalCapacity/numberOfSameZones), math.floor(targetCapacity/numberOfSameZones), floorNum, type, machines)   # ?¿
                    all_areas.append(area)
                    if type == 'CLASE':
                        result = extract_clases(AFORO_CLASES_PATH, area)
                        if result is not None:
                            all_classes.append(result)
                    
                        
                except Exception:
                    
                    area = Area(name, points, 0, 0, floorNum, type, machines) 
                    all_areas.append(area)
                    if type == 'CLASE':
                        result = extract_clases(AFORO_CLASES_PATH, area)
                        if result is not None:
                            all_classes.append(result)
            
            for pared in data[floor]["Walls"]: 
                pared = Boundary(pared, floorNum)
                all_walls.append(pared)
            
            for spawn in data[floor]["Spawns"]:
                spawn = SpawnPoint(spawn["Name"], spawn["Coordinates"], floorNum)
                all_spawns.append(spawn)
            floorNum+=1
                    
        npersons = sum(area.targetCapacity for area in all_areas)
        print(f"Num persons: {npersons}, Entradas: {entrada}, Salidas: {salida}")
        return npersons, all_areas, all_walls, all_spawns, hora