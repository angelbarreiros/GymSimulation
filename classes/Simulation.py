import pandas as pd
import cv2
import numpy as np
import os
import tqdm
from classes.Person import Person

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
                print(f'Area {area.name} has {area.actualCapacity} persons')
                return area
        return None

    def getStairs(self):
        stairs = []
        for floor in self.floors:
            floor_stairs = [area for area in self.target_areas if area.type == 'NOFUNCIONAL' and area.floor == floor]
            if floor_stairs:
                stairs.append(np.random.choice(floor_stairs))
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
            for step, (x, y, floor) in enumerate(person.history):
                data.append({'person_id': person.id, 'step': step, 'x': x, 'y': y, 'floor': floor})
        self.movement_data = pd.DataFrame(data)

    def animate_cv2(self, output_folder='data/animation_frames', total_frames=600):
        def draw_boundary(frame, boundary, color=(0, 0, 0), thickness=10):
            pts = boundary.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness)

        def draw_target_area(frame, area, color=(255, 0, 0), thickness=2):
            pts = area.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
            center = area.points.mean(axis=0).astype(int)
            cv2.putText(frame, f"Area {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 1)
            cv2.putText(frame, f"Aforo {area.targetCapacity}", center-10, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 2)

        def draw_person(frame, x, y, color):
            cv2.circle(frame, (int(x), int(y)), 10, color, -1)

        # Step 1: Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Step 2: Set up the initial frame for all floors
        floor_frames = [cv2.imread(f"data/Planta{i}.png") for i in range(len(self.floors))]
        floor_frames.reverse() 
        height, width = floor_frames[0].shape[:2]

        # Combine the floors into one image
        combined_height = height * len(self.floors)
        combined_frame = np.zeros((combined_height, width, 3), dtype=np.uint8)

        for i, frame in enumerate(floor_frames):
            combined_frame[i*height:(i+1)*height, 0:width] = frame

        # Step 3: Draw the boundaries for all floors
        for boundary in self.boundaries:
            floor_offset = (len(self.floors) - 1 - boundary.floor) * height  # Reverse floor order
            draw_boundary(combined_frame[floor_offset:floor_offset+height, 0:width], boundary)

        # Step 4: Draw target areas for all floors
        for area in self.target_areas:
            floor_offset = (len(self.floors) - 1 - area.floor) * height  # Reverse floor order
            draw_target_area(combined_frame[floor_offset:floor_offset+height, 0:width], area)

        # Step 5: Create color map for persons
        color_map = {person.id: tuple(np.random.randint(0, 255, 3).tolist()) for person in self.persons}

        # Step 6: Generate and save frames with progress bar
        #total_frames = max(person.history[-1][0] for person in self.persons)
        for frame_num in tqdm.tqdm(range(total_frames), desc="Generating frames", unit="frame"):
            current_frame = combined_frame.copy()

            # Update time
            hours = (frame_num // 600) + self.hora
            minutes = (frame_num % 600) // 10
            time_text = f'Time: {hours:02d}:{minutes:02d}'
            text_size = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = text_size[1] + 10
            cv2.putText(current_frame, time_text, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # Plot persons
            for person in self.persons:
                if person.startFrame <= frame_num < person.startFrame + len(person.history):
                    x, y, floor = person.history[frame_num - person.startFrame]
                    floor_offset = (len(self.floors) - 1 - floor) * height  # Reverse floor order
                    draw_person(current_frame[floor_offset:floor_offset+height, 0:width], 
                                x, y, color_map[person.id])

            # Save the frame
            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
            cv2.imwrite(frame_filename, current_frame)