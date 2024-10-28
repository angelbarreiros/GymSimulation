import numpy as np
import subprocess
import os
import utils.date_utils
from classes.Simulation import Simulation
import cProfile
import time
import gc
from utils.global_variables import DEBUG

TOTAL_FRAMES = 600
WEEKDAY_HOURS  = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
WEEKEND_HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
START_DAY = '2024-09-02'
NDAYS = 2
AVERAGE = True

def run_simulation_for_day(day):
    np.random.seed(123)
    hours = WEEKEND_HOURS if utils.date_utils.is_weekend(day) else WEEKDAY_HOURS
    sim = Simulation(hours)
    
    # sim.load_data('data/sim_states/simulation_7.pkl')
    print(f'Creating simulation for {day} and hours {hours}...')
    sim_time, durations = sim.simulate(TOTAL_FRAMES, dia=day, hours=hours, spawn_interval=2, max_spawn=2, average=AVERAGE)
    
    print('Creating animation...')
    anim_time = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES, hours=hours, day=day)

    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    if AVERAGE:
        output_file = f'outputs/{day}_average.mp4'
    else:
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
    return sim_time, anim_time, durations

def main():
    DAYS = utils.date_utils.generate_days(START_DAY, NDAYS, AVERAGE)
    total_start_time = time.time()
    
    for day in DAYS:
        iter_start_time = time.time()
        sim_time, anim_time, durations = run_simulation_for_day(day)
        iter_end_time = time.time()
        print(f"Simulation durations: {durations}, Total: {sum(durations)}, Mean: {np.mean(durations):.2f}, Std: {np.std(durations):.2f}")
        print(f"Iteration for {day} took {iter_end_time - iter_start_time:.2f} seconds (Simulation: {sim_time:.2f} seconds, Animation: {anim_time:.2f} seconds)")
        gc.collect()
    
    total_end_time = time.time()
    print(f"Total time for all iterations: {total_end_time - total_start_time:.2f} seconds")

if __name__ == "__main__":
<<<<<<< Updated upstream
    # if not DEBUG:
    #     cProfile.run('main()')
    # else:
=======
    if DEBUG:
        cProfile.run('main()')
    else:
>>>>>>> Stashed changes
        main()
