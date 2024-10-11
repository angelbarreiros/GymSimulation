import numpy as np
import subprocess
import os
from classes.Simulation import Simulation
from utils.get_info import get_data

TOTAL_FRAMES = 600
def main():
    
    npersons, areas, paredes, spawns, hora = get_data()
    np.random.seed(123)
    print(f"Num persons: {npersons}, Num areas: {len(areas)}, Num walls: {len(paredes)}, Num spawns: {len(spawns)}")

    sim = Simulation(num_persons=npersons, boundary_points=paredes, target_areas=areas, spawn_points=spawns, hora=int(hora))
    
    print('Creating simulation...')
    sim.simulate(TOTAL_FRAMES, spawn_interval=5, max_spawn=2)
    
    print('Creating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES)

    #output_file = 'multi_person_movement.gif'
    output_file = 'multi_person_movement.mp4'
    #subprocess.run(['ffmpeg', '-framerate', '30', '-i', 'data/animation_frames/frame_%04d.png', '-vf', 'scale=800:-1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', output_file], check=True)
    
    subprocess.run([
        'ffmpeg',
        '-framerate', '30',
        '-i', 'data/animation_frames/frame_%04d.png',
        '-c:v', 'libx264',
        '-preset', 'veryslow',
        '-crf', '12',
        '-vf', 'scale=800:-1:flags=lanczos',
        '-pix_fmt', 'yuv420p',
        output_file
    ], check=True)

    print(f"Animation saved as '{output_file}'")

    # for file_path in (os.path.join('data/animation_frames', f) for f in os.listdir('data/animation_frames')):
    #     os.remove(file_path)

if __name__ == "__main__":
    main()
    
    
