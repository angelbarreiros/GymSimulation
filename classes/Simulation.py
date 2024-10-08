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

    # TODO people can't be generated inside too close to other people
    # def initialize_persons(self, num_persons):
    #     persons = []
    #     max_attempts = 1000  # Prevent infinite loop

    #     for i in range(num_persons):
    #         attempts = 0
    #         while attempts < max_attempts:
    #             x = np.random.uniform(self.boundary.get_extents().xmin, self.boundary.get_extents().xmax)
    #             y = np.random.uniform(self.boundary.get_extents().ymin, self.boundary.get_extents().ymax)
                
    #             if all(not area.contains_point(x, y) for area in self.target_areas):
    #                 # Check distance from other persons
    #                 if all(np.sqrt((x - p.x)**2 + (y - p.y)**2) >= 0.2 for p in persons):
    #                     persons.append(PersonMovement(i, x, y))
    #                     break
                
    #             attempts += 1
            
    #         if attempts == max_attempts:
    #             print(f"Warning: Could not place person {i} after {max_attempts} attempts.")

    #     return persons
    def initialize_person(self, num_person, spawn_points, frame):
        spawn_point = np.random.choice(spawn_points)
        self.persons.append(Person(num_person, spawn_point.coords[0], spawn_point.coords[1], frame))
        print(f'Person {num_person} startFrame: {self.persons[-1].startFrame}')

    def simulate(self, frames):
        for frame in tqdm.tqdm(range(frames)):
            print(f'Frame {frame}')
            if frame % 20 == 0 and len(self.persons) < self.npersons:
                print(f'Persons: {len(self.persons)}')
                self.initialize_person(len(self.persons), self.spawn_points, frame)

            for person in self.persons:
                person.move(self.persons, self.boundaries, self.target_areas)
                # for area in self.target_areas:
                #     if area.occupied_by != None:
                #         print(area.occupied_by)

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
        # boundary_points = np.array(self.boundary.xy, dtype=np.int32)

        for boundary in self.boundaries:
            pts = boundary.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=(0, 0, 0), thickness=5)


        # Step 4: Draw target areas
        for area in self.target_areas:
            pts = area.points.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
            center = (int(area.center_x), int(area.center_y))
            cv2.circle(frame, center, 5, (0, 0, 0), -1)
            cv2.putText(frame, f"Area {area.id}", center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 1)
            cv2.putText(frame, f"Aforo {area.aforo}", (int(area.center_x), int(area.center_y-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 0), 2)


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
            cv2.putText(current_frame, text, (text_x, text_y), 
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

            
            # for _, row in current_positions.iterrows():
            #     x, y = int(row['x']), int(row['y'])
            #     color = color_map[row['person_id']]
            #     cv2.circle(current_frame, (x, y), 15, color, -1)

            # for area in self.target_areas:
            #     is_occupied = any(area.contains_point(row['x'], row['y']) for _, row in current_positions.iterrows())
            #     color = (0, 0, 255) if is_occupied else (255, 0, 0)
            #     pt1 = (int(area.x), int(area.y))
            #     pt2 = (int(area.x + area.width), int(area.y + area.height))
            #     cv2.rectangle(current_frame, pt1, pt2, color, thickness=2)

            # Save the frame
            frame_filename = os.path.join(output_folder, f'frame_{frame_num:04d}.png')
            cv2.imwrite(frame_filename, current_frame)
