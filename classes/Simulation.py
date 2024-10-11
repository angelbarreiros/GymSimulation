import pandas as pd
import cv2
import numpy as np
import os
import tqdm
from classes.Person import Person

COLORS = {
    'Red': (0, 0, 255),
    'Green': (0, 255, 0),
    'Blue': (255, 0, 0),
    'Yellow': (0, 255, 255),  # Keeping yellow as is (bright yellow)
    'Cyan': (255, 255, 0),
    'Magenta': (255, 0, 255),
    'White': (255, 255, 255),
    'Black': (0, 0, 0),
    'Gray': (128, 128, 128),
    'Dark Gray': (64, 64, 64),
    'Light Gray': (192, 192, 192),
    'Orange': (0, 140, 255),  # Modified to a deeper orange
    'Purple': (128, 0, 128),
    'Brown': (42, 42, 165),
    'Pink': (203, 192, 255)
}
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
        def draw_boundary(frame, boundary, color=(0, 0, 0), thickness=10):
            pts = boundary.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness)
        def draw_target_area(frame, area, color=(255, 0, 0), thickness=2): 
            pts = area.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
            center = area.points.mean(axis=0).astype(int)
            cv2.putText(frame, f"Area {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 1)
            cv2.putText(frame, f"Aforo {area.targetCapacity}", center-10, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 2)
        def draw_spawn_point(frame, spawn_point, color=(0, 255, 0), thickness=2):
            top_left = (spawn_point.coords[0] - 5, spawn_point.coords[1] - 5)
            bottom_right = (spawn_point.coords[0] + 5, spawn_point.coords[1] + 5)
            top_left = (spawn_point.coords[0] - 10, spawn_point.coords[1] - 10)
            bottom_right = (spawn_point.coords[0] + 10, spawn_point.coords[1] + 10)
            cv2.rectangle(frame, top_left, bottom_right, color, thickness)
            cv2.putText(frame, f"Spawn {spawn_point.name}", (spawn_point.coords[0] + 10, spawn_point.coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        def paint_area(frame, area):
            pts = area.points.reshape((-1, 1, 2))

            if area.totalCapacity == 0:
                fill_color = (0, 0, 255)  # Red
            else:
                n = sum(1 for person in self.persons 
                        if person.target_area == area 
                        and person.startFrame <= frame_num < person.startFrame + len(person.history)
                        and person.history[frame_num - person.startFrame][3] == 'reached')
                occupancy_percent = ( n/ area.totalCapacity) * 100
                if 0 <= occupancy_percent < 20:
                    fill_color = COLORS['Red']  # Red
                elif 20 <= occupancy_percent < 40:
                    fill_color = COLORS['Orange']  # Orange
                elif 40 <= occupancy_percent < 60:
                    fill_color = COLORS['Yellow']  # Yellow
                elif 60 <= occupancy_percent < 80:
                    fill_color = COLORS['Green']  # Green
                else:
                    fill_color = COLORS['Black']  # Black
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts], fill_color)
            alpha = 0.3
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        def paint_noarea(frame, area, color):
            overlay = frame.copy()
            pts = area.points.reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts], color)
            alpha = 0.5
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        def draw_person(frame, x, y, color):
            cv2.circle(frame, (int(x), int(y)), 10, color, -1)

        # Step 1: Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Step 2: Set up
        floor_frames = [cv2.imread(f"data/images/Planta{i}.png") for i in range(len(self.floors))]
        floor_frames.reverse() 
        nfloors = len(self.floors)
        height, width = floor_frames[0].shape[:2]
        header_height = 100 
        color_map = {person.id: tuple(np.random.randint(0, 255, 3).tolist()) for person in self.persons}

        # Combine the floors into one image
        combined_height = (height * nfloors) + header_height
        combined_frame = np.full((combined_height, width, 3), 255, dtype=np.uint8)
        # Copy floor frames to the combined frame
        for i, frame in enumerate(floor_frames):
            combined_frame[header_height + i*height:header_height + (i+1)*height, 0:width] = frame

        # Step 3: Draw the boundaries for all floors
        # for boundary in self.boundaries:
        #     floor_offset = (len(self.floors) - 1 - boundary.floor) * height  # Reverse floor order
        #     draw_boundary(combined_frame[floor_offset:floor_offset+height, 0:width], boundary)

        # Step 4: Draw target areas for all floors
        # for area in self.target_areas:
        #     if area.type == 'NOFUNCIONAL':
        #         continue
        #     floor_offset = (len(self.floors) - 1 - area.floor) * height  # Reverse floor order
        #     draw_target_area(combined_frame[floor_offset:floor_offset+height, 0:width], area)

        # Step 6: Generate and save frames with progress bar
        #total_frames = max(person.history[-1][0] for person in self.persons)

        for frame_num in tqdm.tqdm(range(total_frames), desc="Generating frames", unit="frame"):
            current_frame = combined_frame.copy()

            # Change 'frame' to 'current_frame' in these lines
            time_str = f"Time: {self.hora}:{str(int(frame_num / 10)).zfill(2)[:2]}"
            cv2.putText(current_frame, time_str, (100, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

            current_persons = sum(1 for person in self.persons 
                                if person.startFrame <= frame_num < person.startFrame + len(person.history))
            person_count_str = f"Persons: {current_persons}"
            cv2.putText(current_frame, person_count_str, (width - 600, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)

            # Plot persons
            for person in self.persons:
                if person.startFrame <= frame_num < person.startFrame + len(person.history):
                    x, y, floor, state = person.history[frame_num - person.startFrame]
                    floor_offset = header_height + (len(self.floors) - 1 - floor) * height  # Reverse floor order
                    draw_person(current_frame[floor_offset:floor_offset+height, 0:width], 
                                x, y, color_map[person.id])
            # paint area occupation
            for area in self.target_areas:
                if area.totalCapacity != 0:
                    floor_offset = header_height + (len(self.floors) - 1 - area.floor) * height
                    paint_area(current_frame[floor_offset:floor_offset+height, 0:width], area)
                if area.type=='NOFUNCIONAL':
                    floor_offset = header_height + (len(self.floors) - 1 - area.floor) * height
                    paint_noarea(current_frame[floor_offset:floor_offset+height, 0:width], area, COLORS['Blue'])
                if area.type=='VESTUARIO':
                    floor_offset = header_height + (len(self.floors) - 1 - area.floor) * height
                    paint_noarea(current_frame[floor_offset:floor_offset+height, 0:width], area, COLORS['Purple'])

            for spawn in self.spawn_points:
                floor_offset = header_height + (len(self.floors) - 1 - spawn.floor) * height
                draw_spawn_point(current_frame[floor_offset:floor_offset+height, 0:width], spawn, COLORS['Green'])
            # Save the frame
            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
            cv2.imwrite(frame_filename, current_frame)