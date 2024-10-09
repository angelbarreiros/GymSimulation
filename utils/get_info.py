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

def get_data():
    with open('data/zones.json', 'r') as file:
        data = json.load(file)
        all_areas = []
        all_walls = []
        all_spawns = []
        floorNum=0
        for floor in data:
            hora, entrada, salida = extract_aforo(AFORO_PATH)

            aforo_zonas = extract_aforo_zonas(AFORO_ZONAS_PATH)

            aforo_clases = extract_clases(AFORO_CLASES_PATH)
            
            zones= data[floor]["Zones"]
            for zone in zones:
                
                type = zone["Type"]
                name = zone["Name"]
                points = zone["Coordinates"]
                numberOfSameZones = sum(1 for obj in zones if obj['Type'] == type )
                print(numberOfSameZones)
                
                try:
                    totalCapacity = aforo_zonas.get(type).get('totalCapacity')
                    targetCapacity =  aforo_zonas.get(type).get('targetCapacity')
                    area = Area(name, points, math.floor(totalCapacity/numberOfSameZones), targetCapacity, floorNum, type)   # ?¿
                    all_areas.append(area)
                except Exception:
                    area = Area(name, points, 2, 2, floorNum, type) 
                    all_areas.append(area)
            
            for pared in data[floor]["Walls"]: 
                pared = Boundary(pared, floorNum)
                all_walls.append(pared)

            npersons = entrada-salida

            for spawn in data[floor]["Spawns"]:
                spawn = SpawnPoint(spawn["Name"], spawn["Coordinates"], floorNum)
                all_spawns.append(spawn)
            floorNum+=1


        return npersons, all_areas, all_walls, all_spawns, hora