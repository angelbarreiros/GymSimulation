import pandas as pd
import cv2
import numpy as np
import os
import tqdm
from classes.Person import Person
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils.draw import *

TPLIST = ["EscaleraIzq", "EscaleraDrch", "EscaleraCentroSubida", "EscaleraCentroBajada", "AscensorEsquinaDrch", "AscensorInterior"]

class Simulation:
    def __init__(self, num_persons, boundary_points, target_areas, spawn_points, hora):
        self.boundaries = boundary_points
        self.target_areas = target_areas
        self.spawn_points = spawn_points
        self.persons = []
        self.npersons = num_persons
        self.movement_data = pd.DataFrame()
        self.hora = hora
        self.floors = np.unique([area.floor for area in self.target_areas])

    def getTargetArea(self):
        for area in self.target_areas:
            if area.actualCapacity<area.targetCapacity and area.type!='NOFUNCIONAL':
                area.actualCapacity += 1
                #print(f'Area {area.name} has {area.actualCapacity} persons')
                return area
        return None

    def getStairs(self):
        id = np.random.choice(TPLIST)
        stairs = []
        for area in self.target_areas:
            if area.type == 'NOFUNCIONAL' and area.name==id:
                stairs.append(area)
        #print(f"Stairs: {stairs}")
        return stairs

    def initialize_person(self, num_person, available_spawn_points, frame):
        if not available_spawn_points:
            print(f"No available spawn points for person {num_person} in frame {frame}")
            return False
        
        spawn_point = np.random.choice(available_spawn_points)
        #target_coords = [self.getTargetArea().center_x, self.getTargetArea().center_y]
    
        self.persons.append(Person(num_person, spawn_point.coords[0], spawn_point.coords[1], frame,stairs=self.getStairs(), target_area=self.getTargetArea(), max_step=15, floor=spawn_point.floor))
        available_spawn_points.remove(spawn_point)
        return True

    def simulate(self, frames, spawn_interval=10, max_spawn=1):
        for frame in tqdm.tqdm(range(frames)):
            if frame % spawn_interval == 0 and len(self.persons) < self.npersons:
                available_spawn_points = self.spawn_points.copy()
                spawned_count = 0
                while spawned_count < max_spawn and len(self.persons) < self.npersons:
                    if self.initialize_person(len(self.persons), available_spawn_points, frame):
                        spawned_count += 1
                    else:
                        break 

            for person in self.persons:
                person.move()

        # Collect all movement data
        data = []
        for person in self.persons:
            for step, (x, y, floor, state) in enumerate(person.history):
                data.append({'person_id': person.id, 'step': step, 'x': x, 'y': y, 'floor': floor, 'state': state})
        self.movement_data = pd.DataFrame(data)

    def animate_cv2(self, output_folder='data/animation_frames', total_frames=600):
            start_time = time.time()    
            os.makedirs(output_folder, exist_ok=True)

            floor_frames = [cv2.imread(f"data/images/Planta{i}.png") for i in range(len(self.floors))]
            floor_frames.reverse() 
            nfloors = len(self.floors)
            height, width = floor_frames[0].shape[:2] 
            header_height = 100 
            color_map = {person.id: tuple(np.random.randint(0, 255, 3).tolist()) for person in self.persons}

            combined_height = (height * nfloors) + header_height
            combined_frame = np.full((combined_height, width, 3), 255, dtype=np.uint8)
            for i, frame in enumerate(floor_frames):
                combined_frame[header_height + i*height:header_height + (i+1)*height, 0:width] = frame

            def process_frame(frame_num):
                current_frame = combined_frame.copy()

                time_str = f"Time: {self.hora}:{str(int(frame_num / 10)).zfill(2)[:2]}"
                cv2.putText(current_frame, time_str, (100, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

                current_persons = sum(1 for person in self.persons 
                                    if person.startFrame <= frame_num < person.startFrame + len(person.history))
                person_count_str = f"Persons: {current_persons}"
                cv2.putText(current_frame, person_count_str, (width - 600, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

                for person in self.persons:
                    if person.startFrame <= frame_num < person.startFrame + len(person.history):
                        x, y, floor, state = person.history[frame_num - person.startFrame]
                        floor_offset = header_height + (len(self.floors) - 1 - floor) * height
                        draw_person(current_frame[floor_offset:floor_offset+height, 0:width], 
                                    x, y, color_map[person.id])

                for area in self.target_areas:
                    floor_offset = header_height + (len(self.floors) - 1 - area.floor) * height
                    if area.type == 'NOFUNCIONAL':
                        paint_noarea(current_frame[floor_offset:floor_offset+height, 0:width], area, COLORS['Blue'])
                    elif area.type == 'VESTUARIO':
                        paint_noarea(current_frame[floor_offset:floor_offset+height, 0:width], area, COLORS['Purple'])
                    else:
                        paint_area(current_frame[floor_offset:floor_offset+height, 0:width], area, self.persons, frame_num)

                for spawn in self.spawn_points:
                    floor_offset = header_height + (len(self.floors) - 1 - spawn.floor) * height
                    draw_spawn_point(current_frame[floor_offset:floor_offset+height, 0:width], spawn, COLORS['Green'])

                frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
                cv2.imwrite(frame_filename, current_frame)

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_frame, frame_num) for frame_num in range(total_frames)]
                
                for _ in tqdm.tqdm(as_completed(futures), total=total_frames, desc="Generating frames", unit="frame"):
                    pass

            end_time = time.time()
            total_time = end_time - start_time
            print(f"Total time taken: {total_time:.2f} seconds")
