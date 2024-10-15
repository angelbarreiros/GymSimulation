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


def extract_clases(aforo_clases_path,zone,hora):
    with open(aforo_clases_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for clase in data:
        if clase['studio']==zone.name:

            targetClassArea=Area(zone.name,zone.points,clase['attendingLimit'],clase['bookedAttendees'],3,zone.type,zone.machines)
            newClass = Activity(name=clase['activity'],startDate=clase['startedAt'],endDate=clase['endedAt'],Area=targetClassArea)  
            return newClass


def get_data_initial(path):
    with open(path, 'r') as file:
        data = json.load(file)
   
        all_areas = []
        all_walls = []
        all_spawns = []
        floorNum=0
        for floor in data:
            zones= data[floor]["Zones"]
            for zone in zones:
                type = zone["Type"]
                name = zone["Name"]
                points = zone["Coordinates"]
                machines = zone["Machines"]
                numberOfSameZones = sum(1 for obj in zones if obj['Type'] == type )
                area = Area(name, points,0, 0, floorNum, type, machines)   # ?¿
                all_areas.append(area)
            
            for pared in data[floor]["Walls"]: 
                pared = Boundary(pared, floorNum)
                all_walls.append(pared)
            
            for spawn in data[floor]["Spawns"]:
                spawn = SpawnPoint(spawn["Name"], spawn["Coordinates"], floorNum)
                all_spawns.append(spawn)
            floorNum+=1
                    
        return all_areas, all_walls, all_spawns

def get_data(dia, hora, areas):
    path = f'data/aforo-x-horas/{dia}_{str(hora).zfill(2)}.json'
    print(f"Processing data from {path}")
    
    with open(path, 'r') as file:
        data = json.load(file)
        npersons = 0
        entradas = 0
        salidas = 0
        classes = []
        
        if 'aforo_zonas' in data:
            for zone in data['aforo_zonas']:
                # zone_name = zone['name']
                zone_name = zone['zona']
                matching_area = next((area for area in areas if (area.name == zone_name or area.type == zone_name)), None)
                if matching_area and matching_area.type != 'NOFUNCIONAL' and matching_area.type != 'VESTUARIO' and matching_area.type != 'CLASE':
                    if matching_area.type != matching_area.name:
                        nareas = sum(1 for obj in areas if obj.type == matching_area.type)
                    else:
                        nareas = 1
                    print(f"Matching area {matching_area.name} with {nareas} areas of type {matching_area.type}")
                    matching_area.targetCapacity = int(zone['oc.prom']/nareas)
                    matching_area.totalCapacity = int(zone['aforo']/nareas)
                    npersons += int(zone['oc.prom'])

        if 'classes' in data:
            for clase in data['classes']:
                zone_name = clase['studio']
                matching_area = next((area for area in areas if area.name == zone_name), None)
                if matching_area: # if matching_area.type == 'CLASE':
                    newClass = Activity(name=clase['activity'],startDate=clase['startedAt'],endDate=clase['endedAt'],Area=matching_area)  
                    classes.append(newClass)
                    matching_area.targetCapacity = clase['bookedAttendees']
                    matching_area.totalCapacity = clase['attendingLimit']
                    npersons += clase['bookedAttendees']

        if 'entradas' in data:
            entradas = data['entradas']['entredas']
            salidas = data['entradas']['salidas']

    return npersons, entradas, salidas, areas, classes