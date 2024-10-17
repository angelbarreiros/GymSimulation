import json
import math
from classes.Map import Area, Boundary, SpawnPoint, Activity

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
    path = f'data/formated_data/zones/1_{str(hora).zfill(2)}.json'
    print(f"Processing data from {path}")
    
    with open(path, 'r') as file:
        data = json.load(file)
        data = json.loads(data)
        npersons = 0
        entradas = 0
        salidas = 0
        classes = []
            
        if 'aforo_zonas' in data:
            for zone in data['aforo_zonas']:
                # zone_name = zone['name']
                zone_name = zone['name']
                matching_areas = [area for area in areas if area.type == zone_name]
                if matching_areas and zone_name not in ['NOFUNCIONAL', 'VESTUARIO', 'CLASE']:
                    nareas = len(matching_areas)
                    total_target_capacity = zone['targetCapacity']
                    total_capacity = zone['totalCapacity']
                    base_target_capacity = total_target_capacity // nareas
                    base_total_capacity = total_capacity // nareas
                    remainder_target_capacity = total_target_capacity % nareas
                    remainder_total_capacity = total_capacity % nareas

                    for i, matching_area in enumerate(matching_areas):
                        matching_area.targetCapacity = base_target_capacity
                        matching_area.totalCapacity = base_total_capacity
                        if i < remainder_target_capacity:
                            matching_area.targetCapacity += 1
                        if i < remainder_total_capacity:
                            matching_area.totalCapacity += 1
                        print(f"Matching area {matching_area.name} with {nareas} areas of type {matching_area.type} and {matching_area.targetCapacity} target capacity")
                        npersons += matching_area.targetCapacity

        if 'classes' in data:
            for clase in data['classes']:
                zone_name = clase['studio']
                matching_area = next((area for area in areas if area.name == zone_name), None)
                if matching_area: # if matching_area.type == 'CLASE':
                    newClass = Activity(name=clase['activity'],startDate=clase['startedAt'],endDate=clase['endedAt'],Area=matching_area)  
                    classes.append(newClass)
                    npersons -= matching_area.targetCapacity
                    matching_area.targetCapacity = clase['bookedAttendees']
                    matching_area.totalCapacity = clase['attendingLimit']
                    npersons += clase['bookedAttendees']
                    print(f"Matching area {matching_area.name} with class {clase['activity']} with {clase['bookedAttendees']} attendees")

        if 'entradas' in data:  # NOT WORKING
            for dt in data['entradas']:
                entradas = dt['total_entrada']
                salidas = dt['total_salida']

    return npersons, entradas, salidas, areas, classes