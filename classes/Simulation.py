import pandas as pd
import cv2
import numpy as np
import os
import tqdm
from classes.Person import Person

class Simulation:
    def __init__(self, num_persons, boundary_points, target_areas, spawn_points):
        self.boundaries = boundary_points
        self.target_areas = target_areas
        self.spawn_points = spawn_points
        self.persons = []
        self.npersons = num_persons
        self.movement_data = pd.DataFrame()

    def getTargetArea(self):
        for area in self.target_areas:
            if area.actualCapacity<area.targetCapacity:
                return area
        return None

    def initialize_person(self, num_person, available_spawn_points, frame):
        if not available_spawn_points:
            print(f"No available spawn points for person {num_person} in frame {frame}")
            return False
        
        spawn_point = np.random.choice(available_spawn_points)
        #target_coords = [self.getTargetArea().center_x, self.getTargetArea().center_y]

        self.persons.append(Person(num_person, spawn_point.coords[0], spawn_point.coords[1], frame, target_area=self.getTargetArea(), max_step=15))
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
            for step, (x, y) in enumerate(person.history):
                data.append({'person_id': person.id, 'step': step, 'x': x, 'y': y})
        self.movement_data = pd.DataFrame(data)

    def animate_cv2(self, output_folder='data/animation_frames'):
        # Step 1: Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Step 2: Set up the initial frame
        frame = cv2.imread("data/3.png")
        height, width = frame.shape[:2]

        # Step 3: Draw the boundary
        for boundary in self.boundaries:
            pts = boundary.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=(0, 0, 0), thickness=5)

        # Step 4: Draw target areas
        for area in self.target_areas:
            pts = area.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
            center = area.points.mean(axis=0).astype(int)
            cv2.putText(frame, f"Area {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 1)
            cv2.putText(frame, f"Aforo {area.targetCapacity}", center-10, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 2)

        # Step 5: Create color map for persons
        color_map = {}
        for person_color in range(len(self.persons)):
            color = tuple(np.random.randint(0, 255, 3).tolist())
            color_map[person_color] = color

        # Step 6: Generate and save frames with progress bar
        total_frames = len(self.persons[0].history)
        for frame_num in tqdm.tqdm(range(total_frames), desc="Generating frames", unit="frame"):
            current_frame = frame.copy()

            # Update title
            text = f'Frame {frame_num}'
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = text_size[1] + 2

            hours = (frame_num // 600) + 7
            minutes = (frame_num % 600) // 10
            time_text = f'Time: {hours:02d}:{minutes:02d}'
            text_size = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = text_size[1] + 2
            cv2.putText(current_frame, time_text, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # Plot persons
            current_positions = self.movement_data[self.movement_data['step'] == frame_num]
            for person in self.persons:
                if person.startFrame>frame_num:
                    continue
                if person.startFrame==frame_num:
                    x, y = person.history[person.startFrame-frame_num+1]
                    x, y=int(x), int(y)
                    print(f'Person {person.id} at frame {frame_num}: ({x}, {y})')
                    #print(f'Person {person.id} {person.history}')

                color = color_map[person.id]
                x, y = person.history[frame_num-person.startFrame]
                x, y=int(x), int(y)
                cv2.circle(current_frame, (x, y), 10, color, -1)

            # Save the frame
            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
            cv2.imwrite(frame_filename, current_frame)
