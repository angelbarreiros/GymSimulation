import numpy as np
from utils.shortest_path import a_star_search

class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, max_step=20, target_area=None):
        self.id = person_id
        self.x = start_x
        self.y = start_y
        self.max_step = max_step
        self.history = [(start_x, start_y)]
        self.stay_counter = 0
        self.target_area = target_area
        self.startFrame = startFrame
        self.target_coords = None
        self.route = []

    def move(self):
        if self.target_area:
            if not self.route:
                target_x, target_y = self.target_area.getPointInside()
                self.target_coords = [target_x, target_y]
                self.route = a_star_search((int(self.x), int(self.y)), (target_x, target_y), scale_factor=10, padding=0)
                
                self.x, self.y = self.route.pop(0)

            else:
                
                self.x, self.y = self.route.pop(0)
                
        if self.target_area.contains_point(self.x, self.y):
            self.target_area.actualCapacity += 1
            
        self.history.append((self.x, self.y))

