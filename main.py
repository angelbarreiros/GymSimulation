import numpy as np
import pandas as pd

import tqdm
import os 
import cv2
import json

from classes.simulation import Simulation
from classes.map import Area, Boundary, SpawnPoint
from classes.person import Person
from utils.get_info import extract_aforo, extract_aforo_zonas, extract_clases


def main():
    
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

    # Define seed
    np.random.seed(123)
    print(f"Number of persons: {npersons}")
    # Create simulation with 10 persons
    sim = Simulation(num_persons=npersons, boundary_points=paredes, target_areas=areas, spawn_points=spawns)
    
    # Run simulation for 500 steps
    print('Creating simulation...')
    sim.simulate(200)
    
    # Create and save the animation
    print('\nCreating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames')
    # Create GIF from frames using ffmpeg
    output_gif = 'multi_person_movement.gif'
    os.system(f'ffmpeg -framerate 10 -i data/animation_frames/frame_%04d.png -vf "scale=800:-1" {output_gif}')
    print(f"Animation saved as '{output_gif}'")

    # Delete frames after creating the GIF
    for file_name in os.listdir('data/animation_frames'):
        file_path = os.path.join('data/animation_frames', file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("Temporary frames deleted.")

    #anim.save('multi_person_movement.gif', writer='pillow', fps=30)    
    # # # Save movement data to CSV
    # print('Saving data in csv:')
    # sim.movement_data.to_csv('multi_person_movement_data.csv', index=False)
    # print("Movement data saved as 'multi_person_movement_data.csv'")

if __name__ == "__main__":
    main()
    
    
