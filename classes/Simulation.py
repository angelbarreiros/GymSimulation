import pickle
import pandas as pd
import cv2
import numpy as np
import os
import tqdm
import random
from classes.Person import Person
import time
from utils.draw import *
import math
from utils.get_info import get_data, get_data_initial

TPLIST = ["EscaleraIzq", "EscaleraDrch", "EscaleraCentroSubida", "EscaleraCentroBajada", "AscensorEsquinaDrch", "AscensorInterior"]

class Simulation:
    def __init__(self):
        self.boundaries = None
        # random.shuffle(target_areas)
        self.target_areas = None
        self.spawn_points = None
        self.persons = []
        self.npersons = None
        #self.movement_data = pd.DataFrame()
        self.hora = None
        self.entradas = None
        self.salidas = None
        self.floors = None
        self.classes = []

    def getTargetArea(self):
        # if random.random() < LOCKER_ROOM_PROB:
        #     locker_room_lst = []
        #     for area in self.target_areas:
        #         if area.type == 'VESTUARIO':
        #             locker_room_lst.append(area)
        #     return random.choice(locker_room_lst)
        # random.shuffle(self.target_areas)
        for area in self.target_areas:
            if area.actualCapacity<area.targetCapacity and area.type!='NOFUNCIONAL':
                area.actualCapacity += 1
                print(f'Area {area.name} has {area.actualCapacity} persons')
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

    def load_data(self, filename):
        with open(filename, 'rb') as f:
            state = pickle.load(f)
            self.persons = state['persons']
            self.target_areas = state['areas']
        print(f"Loaded {len(self.persons)} persons and {len(self.target_areas)} areas")

    def get_data_hour(self, dia, hora, areas):
        self.npersons, self.entradas, self.salidas, self.target_areas, classes = get_data(dia, hora, areas)
        self.classes.append(classes)
        self.hora = hora
        self.floors = np.unique([area.floor for area in self.target_areas])
        print(f"Num areas: {len(self.target_areas)}, Num walls: {len(self.boundaries)}, Num spawns: {len(self.spawn_points)}, Num classes: {len(self.classes)}, npersons: {self.npersons}, entradas: {self.entradas}, salidas: {self.salidas}")

    def initialize_person(self, num_person, available_spawn_points, frame, locker_room_prob=.8):
        if not available_spawn_points:
            print(f"No available spawn points for person {num_person} in frame {frame}")
            return False
        
        spawn_point = np.random.choice(available_spawn_points)
        #target_coords = [self.getTargetArea().center_x, self.getTargetArea().center_y]
        
        locker_room = None
        if random.random() < locker_room_prob:
            locker_room_lst = []
            for area in self.target_areas:
                if area.type == 'VESTUARIO':
                    locker_room_lst.append(area)
            locker_room = random.choice(locker_room_lst)
        target=self.getTargetArea()
        if target==None:
            #print(f"No available target areas for person {num_person} in frame {frame}")
            return False
        self.persons.append(Person(num_person, spawn_point.coords[0], spawn_point.coords[1], frame,stairs=self.getStairs(),target_area=target, max_step=15, floor=spawn_point.floor, locker_room=locker_room, max_lifetime= np.random.choice([1, 2, 3])))
        
        available_spawn_points.remove(spawn_point)
        return True
    
    def distribute_targets(self):
        for person in self.persons:
            if person.state!= 'left' and person.lifetime < person.max_lifetime:
                if hasattr(person.target_area, 'actualCapacity'):
                    next(area for area in self.target_areas if area.name == person.target_area.name).actualCapacity -= 1
                person.target_area = self.getTargetArea()
                person.state = None
                person.stay_counter = 0
                person.wait_time = 0
                person.target_coords = None
                person.route = []

    def simulate(self, total_frames, dia='2024-08-05', hours=[7,8], spawn_interval=10, max_spawn=1):
        self.target_areas, self.boundaries, self.spawn_points = get_data_initial('data/zones.json')
        i=-1
        for spawn in self.spawn_points:
            print(f"Spawn {spawn.name} at {spawn.coords}")
        for hora in hours:
            i+=1
            exceeded_lifetime_count = sum(1 for person in self.persons if person.lifetime >= person.max_lifetime)
            for person in self.persons:
                if not hasattr(person.target_area, 'actualCapacity'):
                    continue
                if person.lifetime >= person.max_lifetime:
                    person.target_area.actualCapacity -= 1
                    person.target_area = self.spawn_points[0]
                    person.state = None
                    person.route = None
                    person.locker_room = None
                    print(f'Person {person.id} has exceeded, going to {person.target_area.name}')
                    #person.state = 'left'


            self.get_data_hour(dia, hora, self.target_areas)
            self.distribute_targets()
            nactual_persons = len(self.persons) - exceeded_lifetime_count
            print(f"Hour {hora}: {exceeded_lifetime_count} persons have exceeded their max lifetime")
            
            for frame in tqdm.tqdm(range(total_frames)):  
                if frame % spawn_interval == 0 and nactual_persons <= self.npersons:
                    available_spawn_points = self.spawn_points.copy()
                    spawned_count = 0
                    while spawned_count < max_spawn:
                        if self.initialize_person(len(self.persons), available_spawn_points, (i*total_frames)+frame):
                            spawned_count += 1
                            nactual_persons = len(self.persons) - exceeded_lifetime_count
                            print(f"Hour {hora}:Frame {frame}: {nactual_persons} persons are currently in the building, nperdsons::{self.npersons}")
                        else:
                            break 
                for person in self.persons :
                    person.move()

                # if frame % spawn_interval == 0: #and frame > (frames / len(hours)) / 2:
                #     leaving_persons = [person for person in self.persons if person.lifetime > person.max_lifetime]
                #     for person in leaving_persons:
                #         spawn_point = np.random.choice(self.spawn_points.copy())
                #         person.target_area = spawn_point
                #         person.state = None
                #         self.salidas -= 1
                #         print(f'Person {person.id} is leaving the building')
                        #print(f'Area {person.target_area.name} has {person.target_area.actualCapacity} persons')
            for person in self.persons:
                person.lifetime+=1       
            
        
        # hacer que salgan tantas personas como en self.salidas, segun el stay counter que tengan, (>0)


        # Save the state of the simulation
        # state = {
        #     'persons': [person for person in self.persons],
        #     'areas': [area for area in self.target_areas],
        #     'hora': self.hora
        # }
        # with open(f'data/sim_states/simulation_{self.hora}.pkl', 'wb') as f:
        #     pickle.dump(state, f)

        # Collect all movement data
        # data = []
        # for person in self.persons:
        #     for step, (x, y, floor, state) in enumerate(person.history):
        #         data.append({'person_id': person.id, 'step': step, 'x': x, 'y': y, 'floor': floor, 'state': state})
        # self.movement_data = pd.DataFrame(data)

    def animate_cv2(self, output_folder='data/animation_frames', total_frames=600, hours=[7, 8]):
        start_time = time.time()    
        os.makedirs(output_folder, exist_ok=True)
        floor_frames = [cv2.imread(f"data/images/Planta{i}.png") for i in range(len(self.floors))]
        nfloors = len(self.floors)
        height, width = floor_frames[0].shape[:2] 
        header_height = 100 

        # Calculate the dimensions for the square layout
        grid_size = math.ceil(math.sqrt(nfloors))
        combined_width = width * grid_size 
        combined_height = (height * grid_size) + header_height
        print(f"Combined width: {combined_width}, Combined height: {combined_height}")
        combined_frame = np.full((combined_height, combined_width, 3), 255, dtype=np.uint8)
        for i, frame in enumerate(floor_frames):
            row = i // grid_size
            col = i % grid_size
            y_start = header_height + row * height
            x_start = col * width
            combined_frame[y_start:y_start+height, x_start:x_start+width] = frame

        draw_colorLegend(combined_frame)

        def process_frame(frame_num):
            current_frame = combined_frame.copy()
            minutes = int(frame_num / 10)  # Assuming each frame represents 0.1 seconds
            hours_good = (self.hora + minutes // 60 ) - len(hours) +1# carefulllllll
            minutes = minutes % 60
            time_str = f"Time: {hours_good:02d}:{minutes:02d}"
            cv2.putText(current_frame, time_str, (100, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

            current_persons = sum(1 for person in self.persons 
                                if person.startFrame <= frame_num < person.startFrame + len(person.history))
            person_count_str = f"Persons: {current_persons}"
            cv2.putText(current_frame, person_count_str, (combined_width - 600, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

            for person in self.persons:
                if (person.startFrame <= frame_num < person.startFrame + len(person.history)):
                    x, y, floor, state, target = person.history[frame_num - person.startFrame]
                    # if state == 'left':
                    #     continue
                    row = floor // grid_size
                    col = floor % grid_size
                    floor_offset_y = header_height + row * height
                    floor_offset_x = col * width
                    draw_person(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], x, y, COLORS['Black'])

            for wall in self.boundaries:
                row = wall.floor // grid_size
                col = wall.floor % grid_size
                floor_offset_y = header_height + row * height
                floor_offset_x = col * width
                draw_boundary(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], wall)

            for area in self.target_areas:
                row = area.floor // grid_size
                col = area.floor % grid_size
                floor_offset_y = header_height + row * height
                floor_offset_x = col * width
                if area.type == 'NOFUNCIONAL':
                    paint_noarea(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], area, COLORS['Blue'])
                elif area.type == 'VESTUARIO':
                    paint_noarea(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], area, COLORS['Purple'])
                else:
                    paint_area(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], area, self.persons, frame_num)

            for classe in self.classes[frame_num//total_frames]:
                row = classe.Area.floor // grid_size
                col = classe.Area.floor % grid_size
                floor_offset_y = header_height + row * height
                floor_offset_x = col * width
                draw_class(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], classe, COLORS['Black'])
            
            for spawn in self.spawn_points:
                row = spawn.floor // grid_size
                col = spawn.floor % grid_size
                floor_offset_y = header_height + row * height
                floor_offset_x = col * width
                draw_spawn_point(current_frame[floor_offset_y:floor_offset_y+height, floor_offset_x:floor_offset_x+width], spawn, COLORS['Green'])

            draw_legend(current_frame, self.target_areas, self.persons, frame_num)
            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
            cv2.imwrite(frame_filename, current_frame)
            # print(f"Frame {frame_num} saved to {frame_filename}")

        
        # for frame_num in tqdm.tqdm(range(total_frames * len(hours)), desc="Generating frames", unit="frame"):
        #     process_frame(frame_num)


        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_frame, frame_num) for frame_num in range(total_frames*len(hours))]
            
            for _ in tqdm.tqdm(as_completed(futures), total=total_frames*len(hours), desc="Generating frames", unit="frame"):
                pass

        # import multiprocessing
        # # with Pool() as pool:
        # #     results = list(tqdm.tqdm(
        # #         pool.imap(process_frame, range(total_frames * len(hours))),
        # #         total=total_frames * len(hours),
        # #         desc="Generating frames",
        # #         unit="frame"
        # #     ))
        # print(multiprocessing.cpu_count())
        # with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        #     with tqdm(total=total_frames * len(hours), desc="Generating frames", unit="frame") as pbar:
        #         for _ in pool.imap_unordered(process_frame, range(total_frames * len(hours))):
        #             pbar.update()

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time taken: {total_time:.2f} seconds")