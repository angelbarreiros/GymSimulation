import numpy as np
from utils.shortest_path import create_matrix_from_json, a_star_search_from_grid

SCALE_FACTOR = 10
MATRIX_FLOOR = [create_matrix_from_json(floor, SCALE_FACTOR, 1) for floor in range(3)]

class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, stairs, max_step=20, target_area=None, floor=0):
        self.id = person_id
        self.x = start_x
        self.y = start_y
        self.current_floor = floor
        self.max_step = max_step
        self.history = [(start_x, start_y, self.current_floor, None)]
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
        #if np.random.rand() < 0.8: # pasar x los vestuarios
        #print(f"Person {self.id} is ({self.state}, on {self.target_area.name if self.target_area else 'None'}")
        if self.target_area:
            if not self.route:  # calcular ruta si no tiene
                if self.state==None:  # primera vez o acaba de llegar al piso destino
                    if self.target_area.floor != self.current_floor:  # target is not in this floor -> go to stairs
                        self.target_coords = self.stairs[self.current_floor].getPointInside()
                        self.state = 'moving_stairs'
                    else:  # target on this floor -> go to it
                        self.target_coords = self.target_area.getPointInside()
                        self.state = 'moving_target'
                    # print(self.x, self.y, self.target_coords)
                    # self.route = self.getEasyRoute((int(self.x), int(self.y)), self.target_coords, step=10)
                    # self.route = a_star_search((int(self.x), int(self.y)), self.target_coords, f"Planta{self.current_floor}", padding=0, scale_factor=5)
                    self.route = a_star_search_from_grid(grid=MATRIX_FLOOR[self.current_floor], 
                                                         src=(int(self.x), int(self.y)), dest=self.target_coords,
                                                         scale_factor=SCALE_FACTOR, debug=True)
                    self.x, self.y = self.route.pop(0)  # move to next cell in route in any case

                elif self.state == 'moving_stairs': # if stairs, go to destination floor
                    self.current_floor = self.target_area.floor
                    # change to spawn on that floor
                    self.x, self.y = self.stairs[self.current_floor].getPointInside()
                    self.state = None
                elif self.state == 'moving_target': # if target, finish
                    #self.target_area.actualCapacity += 1 # already on simulation
                    #self.target_area = None
                    self.state = 'reached'
                elif self.state == 'reached':
                    self.stay_counter += 1
            else:
                self.x, self.y = self.route.pop(0)
        #print(f"Person {self.id} is ({self.state}, on {self.target_area.name if self.target_area else 'None'}, at {self.x}, {self.y}, floor {self.current_floor})")
        self.history.append((self.x, self.y, self.current_floor, self.state))

