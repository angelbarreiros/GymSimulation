import numpy as np
import os 

from classes.Simulation import Simulation
from utils.get_info import get_data


def main():
    TOTAL_FRAMES = 200
    npersons, areas, paredes, spawns = get_data()
    np.random.seed(123)
    print(f"Num persons: {npersons}, Num areas: {len(areas)}, Num walls: {len(paredes)}, Num spawns: {len(spawns)}")

    sim = Simulation(num_persons=npersons, boundary_points=paredes, target_areas=areas, spawn_points=spawns)
    
    print('Creating simulation...')
    sim.simulate(TOTAL_FRAMES)
    
    print('Creating animation...')
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

if __name__ == "__main__":
    main()
    
    
