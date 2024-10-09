import numpy as np

class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, max_step=20, target_area=None, floor=0):
        self.id = person_id
        self.x = start_x
        self.y = start_y
        self.current_floor = floor
        self.max_step = max_step
        self.history = [(start_x, start_y, self.current_floor)]
        self.stay_counter = 0
        self.target_area = target_area
        self.startFrame = startFrame
        self.target_coords = None

    def move(self):
        if self.target_area:

            target_x, target_y = self.target_area.getPointInside()
            self.target_coords = [target_x, target_y]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = np.sqrt(dx**2 + dy**2)

            step = min(self.max_step, distance)
            self.x = self.x + dx * step / distance
            self.y = self.y + dy * step / distance

            if self.target_area.contains_point(self.x, self.y):
                self.target_area.actualCapacity += 1
                
        self.history.append((self.x, self.y, self.current_floor))

