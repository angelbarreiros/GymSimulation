import numpy as np
from utils.shortest_path import a_star_search

class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, stairs, max_step=20, target_area=None, floor=0):
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
        self.route = []
        self.stairs = stairs
        self.state = None # 'moving_target', 'reached', 'moving_stairs'

    def getEasyRoute(self, start, end, step=10):
        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0
        distance = np.sqrt(dx**2 + dy**2)
        n_steps = int(distance/step)
        x_step = dx/n_steps
        y_step = dy/n_steps
        route = [(int(x0 + i*x_step), int(y0 + i*y_step)) for i in range(1, n_steps)]
        route.append((x1, y1))  # Ensure the final step reaches the exact end point
        return route

    def move(self):
        if self.target_area:
            if not self.route:  # calcular ruta si no tiene
                if self.state==None:  # primera vez o acaba de llegar al piso destino
                    if self.target_area.floor != self.current_floor:  # target is not in this floor -> go to stairs
                        target_x, target_y = self.stairs[self.current_floor].getPointInside()
                        self.target_coords = (target_x, target_y)
                        #self.route = a_star_search((int(self.x), int(self.y)), self.target_coords, f"Planta{self.current_floor}", padding=0, scale_factor=5)
                        self.route = self.getEasyRoute((int(self.x), int(self.y)), self.target_coords, step=10)
                        self.state = 'moving_stairs'
                    else:  # target on this floor -> go to it
                        target_x, target_y = self.target_area.getPointInside()
                        self.target_coords = (target_x, target_y)
                        #self.route = a_star_search((int(self.x), int(self.y)), self.target_coords, f"Planta{self.current_floor}", padding=0, scale_factor=5)
                        self.route = self.getEasyRoute((int(self.x), int(self.y)), self.target_coords, step=10)
                        self.state = 'moving_target'
                    self.x, self.y = self.route.pop(0)  # move to next cell in route in any case

                elif self.state == 'moving_stairs': # if stairs, go to destination floor
                    self.current_floor = self.target_area.floor
                    # change to spawn on that floor
                    self.x, self.y = self.stairs[self.current_floor].getPointInside()
                    self.state = None
                elif self.state == 'moving_target': # if target, finish
                    #self.target_area.actualCapacity += 1 # already on simulation
                    self.target_area = None
                    self.state = 'reached'
            else:
                self.x, self.y = self.route.pop(0)
        #print(f"Person {self.id} is ({self.state}, on {self.target_area.name if self.target_area else 'None'}, at {self.x}, {self.y}, floor {self.current_floor})")
        self.history.append((self.x, self.y, self.current_floor))

