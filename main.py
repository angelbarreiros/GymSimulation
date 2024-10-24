import numpy as np
import subprocess
import os
import utils.date_utils
from classes.Simulation import Simulation
import cProfile
from utils.global_variables import DEBUG

TOTAL_FRAMES = 600
WEEKDAY_HOURS  = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
WEEKEND_HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
START_DAY = '2024-09-03'
NDAYS = 14

def run_simulation_for_day(day):
    np.random.seed(123)
    hours = WEEKEND_HOURS if utils.date_utils.is_weekend(day) else WEEKDAY_HOURS
    sim = Simulation(hours)
    
    # sim.load_data('data/sim_states/simulation_7.pkl')

    print(f'Creating simulation for {day} and hours {hours}...')
    sim.simulate(TOTAL_FRAMES, dia=day, hours=hours, spawn_interval=3, max_spawn=2)
    
    print('Creating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES, hours=hours, day=day)

    output_file = f'outputs/{day}.mp4'
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
    del sim

def main():
    
    DAYS = utils.date_utils.generate_days(START_DAY, NDAYS)
    for day in DAYS:
        try:
            run_simulation_for_day(day)
        except Exception as e:
            print(f"Error processing day {day}: {str(e)}")
            continue
        
        # Force garbage collection after each simulation
        import gc
        gc.collect()

if __name__ == "__main__":
    if DEBUG:
        cProfile.run('main()')
    else:
        main()
