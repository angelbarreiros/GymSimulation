import numpy as np
import subprocess
import os
from classes.Simulation import Simulation

TOTAL_FRAMES = 600
HOURS = [8, 9]#, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
DAYS = ['2024-09-02']#, '2024-09-03']  # Add more days as needed

def run_simulation_for_day(day):
    np.random.seed(123)
    sim = Simulation(HOURS)
    
    # sim.load_data('data/sim_states/simulation_7.pkl')

    print(f'Creating simulation for {day}...')
    sim.simulate(TOTAL_FRAMES, dia=day, hours=HOURS, spawn_interval=3, max_spawn=2)
    
    print('Creating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES, hours=HOURS, day=day)

    output_file = f'outputs/full_{day}.mp4'
    subprocess.run([
        'ffmpeg', '-y', 
        '-framerate', '30', 
        '-i', 'data/animation_frames/frame_%04d.jpg',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-vf', 'format=yuv420p,scale=1920:-2:flags=lanczos',
        '-movflags', '+faststart',
        '-profile:v', 'high',
        '-level', '4.2',
        '-loglevel', 'info',
        output_file
    ], check=True)

    print(f"Animation saved as '{output_file}'")

    for file_path in (os.path.join('data/animation_frames', f) for f in os.listdir('data/animation_frames')):
        os.remove(file_path)

def main():
    for day in DAYS:
        run_simulation_for_day(day)

if __name__ == "__main__":
    # cProfile.run('main()')
    main()
