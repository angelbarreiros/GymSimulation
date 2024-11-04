import json
import math
from classes.Map import Area, Boundary, SpawnPoint, Activity
from utils.global_variables import DEBUG

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

def get_data(dia, hora, areas, average):
    if average:
        path = f'data/formated_data/averageZones/{dia}_{str(hora).zfill(2)}.json'
    else:
        path = f'data/formated_data/zones/{dia}_{str(hora).zfill(2)}.json'
    print(f"Processing data from {path}")
    
    with open(path, 'r') as file:
        data = json.load(file)
        #data = json.loads(data)
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
                        if DEBUG:
                            print(f"Matching area {matching_area.name} with {nareas} areas of type {matching_area.type} and {matching_area.targetCapacity} target capacity")
                        npersons += matching_area.targetCapacity
                    for studio in ['Studio 4', 'Studio 1', 'Studio 2', 'Studio 3']:
                        matching_studio = next((area for area in areas if area.name == studio), None)
                        if matching_studio:
                            matching_studio.targetCapacity = 0
                            matching_studio.totalCapacity = 0

        if 'aforo_clases' in data:
            for clase in data['aforo_clases']:
                zone = clase['zone']
                matching_area = next((area for area in areas if area.name == zone), None)
                if matching_area:
                    npersons -= matching_area.targetCapacity
                    matching_area.targetCapacity = clase['targetCapacity']
                    matching_area.totalCapacity = clase['totalCapacity']
                    npersons += clase['targetCapacity']
                    act = Activity(name=clase['name'],startDate=clase['hour'],totalCapacity=clase['totalCapacity'], Area=matching_area)  #,endDate= clase['hour']
                    classes.append(act)
                    if DEBUG:
                        print(f"Matching area {act.Area.name} with class {act.name} with {matching_area.targetCapacity} and {matching_area.totalCapacity} capacity")

        if 'entradas' in data:  # NOT in json
            for dt in data['entradas']:
                entradas = dt['total_entrada']
                salidas = dt['total_salida']

        # for studio in ['Studio 4', 'Studio 1', 'Studio 2', 'Studio 3']:
        #     matching_studio = next((area for area in areas if area.name == studio), None)
        #     if matching_studio:
        #         print(f"Studio {matching_studio.name} has target capacity {matching_studio.targetCapacity} and total capacity {matching_studio.totalCapacity}")

    return npersons, entradas, salidas, areas, classes