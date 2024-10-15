import numpy as np
import subprocess
import os
from classes.Simulation import Simulation

TOTAL_FRAMES = 600
def main():
    
    np.random.seed(123)

    sim = Simulation()
    
    #sim.load_data('data/sim_states/simulation_7.pkl')

    print('Creating simulation...')
    sim.simulate(TOTAL_FRAMES, hours=[8], spawn_interval=5, max_spawn=2)
    
    print('Creating animation...')
    anim = sim.animate_cv2(output_folder='data/animation_frames', total_frames=TOTAL_FRAMES, hours=[8])

    #output_file = 'multi_person_movement.gif'
    output_file = 'multi_person_movement.mp4'
    #subprocess.run(['ffmpeg', '-framerate', '30', '-i', 'data/animation_frames/frame_%04d.png', '-vf', 'scale=800:-1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', output_file], check=True)
                
    subprocess.run([
        'ffmpeg',
        '-framerate', '30',
        '-i', 'data/animation_frames/frame_%04d.png',
        '-c:v', 'libx264',
        '-preset', 'veryslow',
        '-crf', '17',
        '-vf', 'scale=1920:-2:flags=lanczos,fps=60',
        '-pix_fmt', 'yuv420p',
        '-b:v', '10M',
        '-maxrate', '15M',
        '-bufsize', '20M',
        '-movflags', '+faststart',
        '-profile:v', 'high',
        '-level', '4.2',
        output_file
    ], check=True)

    print(f"Animation saved as '{output_file}'")

    # for file_path in (os.path.join('data/animation_frames', f) for f in os.listdir('data/animation_frames')):
    #     os.remove(file_path)

if __name__ == "__main__":
    main()
    
    
