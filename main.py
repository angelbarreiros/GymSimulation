import numpy as np
import subprocess
import cProfile
from classes.Simulation import Simulation

TOTAL_FRAMES = 600
HOURS = [7,8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
DIA = '2024-09-02'
def main():
    np.random.seed(123)
    sim = Simulation()
    
    # sim.load_data('data/sim_states/simulation_7.pkl')

    print('Creating simulation...')
    sim.simulate(TOTAL_FRAMES, dia=DIA, hours=HOURS, spawn_interval=3, max_spawn=2)
    
    print('Creating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES, hours=HOURS)

    #output_file = 'multi_person_movement.gif'
    output_file = 'multi_person_movement.mp4'
    #subprocess.run(['ffmpeg', '-framerate', '30', '-i', 'data/animation_frames/frame_%04d.png', '-vf', 'scale=800:-1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', output_file], check=True)
                
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

    import os
    for file_path in (os.path.join('data/animation_frames', f) for f in os.listdir('data/animation_frames')):
        os.remove(file_path)

if __name__ == "__main__":
    # cProfile.run('main()')
    main()    
    
