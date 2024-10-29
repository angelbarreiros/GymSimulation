from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
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
from utils.global_variables import DEBUG

TPLIST = ["EscaleraIzq", "EscaleraDrch", "EscaleraCentroSubida", "EscaleraCentroBajada", "AscensorInterior"]

class Simulation:
    def __init__(self, hours):
        self.boundaries = None
        # random.shuffle(target_areas)
        self.target_areas = None
        self.spawn_points = None
        self.persons = []
        self.npersons = None
        #self.movement_data = pd.DataFrame()
        self.hora = None
        self.hours = hours
        self.entradas = None
        self.salidas = None
        self.floors = None
        self.classes = []
        self.personsDeleted = []

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
                if DEBUG:
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
        if DEBUG:
            print(f"Loaded {len(self.persons)} persons and {len(self.target_areas)} areas")

    def get_data_hour(self, dia, hora, areas, average):
        self.npersons, self.entradas, self.salidas, self.target_areas, classes = get_data(dia, hora, areas, average)
        # self.npersons = 500
        self.classes.append(classes)
        self.hora = hora
        self.floors = np.unique([area.floor for area in self.target_areas])
        if DEBUG:
            print(f"Num areas: {len(self.target_areas)}, Num walls: {len(self.boundaries)}, Num spawns: {len(self.spawn_points)}, Num classes: {len(self.classes)}, npersons: {self.npersons}, entradas: {self.entradas}, salidas: {self.salidas}")

    def initialize_person(self, num_person, available_spawn_points, frame, locker_room_prob=.3):
        if not available_spawn_points:
            if DEBUG:
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
        if target.floor == 3:
            max_time=1
        else:
            probabilities = [0.3, 0.5, 0.15, 0.05]
            max_time = np.random.choice([1, 2, 3, 4], p=probabilities)
        self.persons.append(Person(num_person, spawn_point.coords[0], spawn_point.coords[1], frame,stairs=self.getStairs(),target_area=target, max_step=15, floor=spawn_point.floor, locker_room=locker_room, max_lifetime=max_time))
        
        available_spawn_points.remove(spawn_point)
        return True
    
    def simulate(self, total_frames, dia='2024-08-05', hours=[7,8], spawn_interval=10, max_spawn=1, average=False):
        start_time = time.time()
        self.target_areas, self.boundaries, self.spawn_points = get_data_initial('data/zones.json')
        i=-1
        durations = []
        for spawn in self.spawn_points:
            if DEBUG:
                print(f"Spawn {spawn.name} at {spawn.coords}")
        for hora in hours:
            start_time_hour = time.time()
            i+=1
            self.get_data_hour(dia, hora, self.target_areas, average)
            exceeded_lifetime_count = 0
            idx = 0
            for person in self.persons:
                person.lifetime+=1
                
                # Deleted person
                if not hasattr(person.target_area, 'actualCapacity') or person.state == 'left':
                    self.personsDeleted.append(self.persons.pop(idx))
                    continue
                
                # Leave the building
                elif person.lifetime >= person.max_lifetime:
                    exceeded_lifetime_count += 1
                    person.target_area.actualCapacity -= 1
                    person.target_area = self.spawn_points[0]
                    # person.wait_time = 0
                    person.state = None
                    person.route = None
                    person.locker_room = None
                    if DEBUG:
                        print(f'Person {person.id} has exceeded, going to {person.target_area.name}')
                    #person.state = 'left'
                    
                else:
                    # if hasattr(person.target_area, 'actualCapacity'):
                    #     next(area for area in self.target_areas if area.name == person.target_area.name).actualCapacity -= 1
                    if person.target_area.actualCapacity > person.target_area.targetCapacity:
                        person.target_area.actualCapacity -= 1
                        person.target_area = self.getTargetArea()
                        person.state = None
                        person.stay_counter = 0
                        person.wait_time = 0
                        person.target_coords = None
                        person.route = None
                        person.locker_room = None
                        
                idx += 1
                            
            nactual_persons = len(self.persons) - exceeded_lifetime_count
            if DEBUG:
                print(f"Hour {hora}: {exceeded_lifetime_count} persons have exceeded their max lifetime")
            
            for frame in tqdm.tqdm(range(total_frames)):  
                if frame % spawn_interval == 0 and nactual_persons <= self.npersons:
                    available_spawn_points = self.spawn_points.copy()
                    spawned_count = 0
                    while spawned_count < max_spawn:
                        if self.initialize_person(len(self.persons), available_spawn_points, (i*total_frames)+frame):
                            spawned_count += 1
                            nactual_persons = len(self.persons) - exceeded_lifetime_count
                            if DEBUG:
                                print(f"Hour {hora}:Frame {frame}: {nactual_persons} persons are currently in the building, npersons:{self.npersons}")
                        else:
                            break
                         
                for person in self.persons :
                    person.move()
            end_time_hour = time.time()
            durations.append(end_time_hour - start_time_hour)

                    
        self.persons += self.personsDeleted
        end_time = time.time()
        return end_time - start_time, durations
                
    def _process_batch(self, batch_data):
        """Process a batch of frames and return them as compressed data"""
        frames_data, batch_start = batch_data
        results = []
        
        for i, frame_data in enumerate(frames_data):
            frame_num = batch_start + i
            (base_frame, grid_size, height, width, header_height, 
             combined_width, total_frames) = frame_data
            
            current_frame = base_frame.copy()
            
            # Time calculations
            minutes = int(frame_num / 10)
            hours_good = (self.hora + minutes // 60) - len(self.hours) + 1
            minutes = minutes % 60
            time_str = f"Time: {hours_good:02d}:{minutes:02d}"

            # Text rendering
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.5
            font_thickness = 3
            
            text_size = cv2.getTextSize(time_str, font, font_scale, font_thickness)[0]
            text_x = (combined_width - text_size[0]) // 2
            cv2.putText(current_frame, time_str, (text_x, 200), font, font_scale, (0, 0, 0), font_thickness)

            current_persons = 0
            left_persons = 0
            # Draw active persons
            for person in self.persons:
                if person.startFrame <= frame_num < person.startFrame + len(person.history):
                    x, y, floor, state, target = person.history[frame_num - person.startFrame]
                    floor_offset_y = header_height + (floor // grid_size) * height
                    floor_offset_x = (floor % grid_size) * width
                    if state == 'left':
                        left_persons += 1
                    else:
                        current_persons += 1
                        if state == 'reached':
                            color = COLORS['Black']      
                        elif state == 'moving_lockers':
                            color = COLORS['Purple']  
                        elif target == 'EntradaParking' or target == 'EntradaInicial':
                            color = COLORS['Red']
                        else:
                            color = COLORS['Blue']          # White for default

                        # Draw person as filled circle
                        draw_person(current_frame[floor_offset_y:floor_offset_y+height, 
                                floor_offset_x:floor_offset_x+width], x, y, color)


            person_count_str = f"Persons: {current_persons}"
            text_size = cv2.getTextSize(person_count_str, font, font_scale-1, font_thickness-1)[0]
            text_x = (combined_width - text_size[0]) // 2
            cv2.putText(current_frame, person_count_str, (text_x-75, 320), font, font_scale, (0, 0, 0), font_thickness)

            # Draw walls
            for wall in self.boundaries:
                floor_offset_y = header_height + (wall.floor // grid_size) * height
                floor_offset_x = (wall.floor % grid_size) * width
                draw_boundary(current_frame[floor_offset_y:floor_offset_y+height, 
                            floor_offset_x:floor_offset_x+width], wall)

            # Draw areas
            for area in self.target_areas:
                floor_offset_y = header_height + (area.floor // grid_size) * height
                floor_offset_x = (area.floor % grid_size) * width
                if area.type == 'NOFUNCIONAL':
                    paint_noarea(current_frame[floor_offset_y:floor_offset_y+height, 
                               floor_offset_x:floor_offset_x+width], area, COLORS['Blue'])
                elif area.type == 'VESTUARIO':
                    paint_noarea(current_frame[floor_offset_y:floor_offset_y+height, 
                               floor_offset_x:floor_offset_x+width], area, COLORS['Purple'])
                else:
                    paint_area(current_frame[floor_offset_y:floor_offset_y+height, 
                              floor_offset_x:floor_offset_x+width], area, self.persons, frame_num)

            # Draw classes
            for classe in self.classes[frame_num//total_frames]:
                floor_offset_y = header_height + (classe.Area.floor // grid_size) * height
                floor_offset_x = (classe.Area.floor % grid_size) * width
                draw_class(current_frame[floor_offset_y:floor_offset_y+height, 
                          floor_offset_x:floor_offset_x+width], classe, COLORS['Black'])

            # Compress frame using JPEG format
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # 90% quality
            _, compressed = cv2.imencode('.jpg', current_frame, encode_param)
            results.append((frame_num, compressed))

        return results

    def animate_cv2(self, output_folder='data/animation_frames', total_frames=600, hours=[7, 8], day='2024-08-05'):
        os.makedirs(output_folder, exist_ok=True)
        self.hours = hours
        start_time = time.time()
        
        # Pre-load and cache all floor frames
        floor_frames = [cv2.imread(f"data/images/Planta{i}.png") for i in range(len(self.floors))]
        nfloors = len(self.floors)
        height, width = floor_frames[0].shape[:2]
        header_height = 100

        # Calculate grid layout once
        grid_size = math.ceil(math.sqrt(nfloors))
        combined_width = width * grid_size
        combined_height = (height * grid_size) + header_height
        
        # Create base frame with all static elements
        base_frame = np.full((combined_height, combined_width, 3), 255, dtype=np.uint8)
        
        # Draw static elements once
        for i, frame in enumerate(floor_frames):
            row = i // grid_size
            col = i % grid_size
            y_start = header_height + row * height
            x_start = col * width
            base_frame[y_start:y_start+height, x_start:x_start+width] = frame

        # Pre-draw spawn points
        for spawn in self.spawn_points:
            row = spawn.floor // grid_size
            col = spawn.floor % grid_size
            floor_offset_y = header_height + row * height
            floor_offset_x = col * width
            draw_spawn_point(base_frame[floor_offset_y:floor_offset_y+height, 
                            floor_offset_x:floor_offset_x+width], spawn, COLORS['Green'])


        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        font_thickness = 3
        day_str = f"Day: {day}"
        day_text_size = cv2.getTextSize(day_str, font, font_scale, font_thickness)[0]
        day_text_x = (combined_width - day_text_size[0]) // 2
        cv2.putText(base_frame, day_str, (day_text_x, 75), font, font_scale, (0, 0, 0), font_thickness)

        # single threaded or multi-threaded processing
        if False:
            total_frames_count = total_frames * len(hours)
            frames_data = [
            (base_frame, grid_size, height, width, header_height, 
             combined_width, total_frames)
            for _ in range(total_frames_count)
            ]

            with tqdm.tqdm(total=total_frames_count, desc="Generating frames", unit="frame") as pbar:
                for frame_num, frame_data in enumerate(frames_data):
                    batch_results = self._process_batch(([frame_data], frame_num))
                    for _, compressed_frame in batch_results:
                        frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.jpg')
                        with open(frame_filename, 'wb') as f:
                            f.write(compressed_frame)
                        pbar.update(1)
        else:
            # Prepare batches
            BATCH_SIZE = 100
            total_frames_count = total_frames * len(hours)
            batches = []
            
            for batch_start in range(0, total_frames_count, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_frames_count)
                batch_frames = [
                    (base_frame, grid_size, height, width, header_height, 
                    combined_width, total_frames)
                    for _ in range(batch_start, batch_end)
                ] 
                batches.append((batch_frames, batch_start))

            # Process batches with ThreadPoolExecutor
            num_workers = os.cpu_count()-1
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                for batch_data in batches:
                    future = executor.submit(self._process_batch, batch_data)
                    futures.append(future)
                
                # Process and write results as they complete
                with tqdm.tqdm(total=total_frames_count, desc="Generating frames", unit="frame") as pbar:
                    for future in as_completed(futures):
                        batch_results = future.result()
                        for frame_num, compressed_frame in batch_results:
                            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.jpg')
                            with open(frame_filename, 'wb') as f:
                                f.write(compressed_frame)
                            pbar.update(1)
        
        end_time = time.time()
        return end_time - start_time