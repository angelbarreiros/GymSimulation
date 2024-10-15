import numpy as np
from utils.shortest_path import create_matrix_from_json, a_star_search_from_grid
from utils.fixed_route import join_coordinates
import random

SCALE_FACTOR = 10
MATRIX_FLOOR = [create_matrix_from_json(floor, SCALE_FACTOR, 1) for floor in range(4)]

LANE_POINTS = [[[753, 440],[753,470],[1386,470],[1386,440]],[[753, 388],[753,418],[1386,418],[1386,388]],[[753, 336],[753,366],[1386,366],[1386,336]],[[753, 284],[753,314],[1386,314],[1386,284]],[[753, 232],[753,262],[1386,262],[1386,232]], [[753, 180],[753,210],[1386,210],[1386,180]]]
POOL_LANES = [join_coordinates(LANE_POINTS[i], max_step=(i)*3+1) for i in range(len(LANE_POINTS))]


class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, stairs, max_step=20, target_area=None, floor=0, locker_room=None):
        self.id = person_id
        self.x = start_x
        self.y = start_y
        self.current_floor = floor
        self.max_step = max_step
        self.locker_room = locker_room
        self.history = [(start_x, start_y, self.current_floor, None)]
        self.stay_counter = 0
        self.wait_time = 0
        self.target_area = target_area
        self.startFrame = startFrame
        self.target_coords = None
        self.route = []
        self.stairs = stairs
        self.state = None # 'moving_target', 'reached', 'moving_stairs'
        self.guided_route_idx = 0 # e.g. pool        

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
            if self.wait_time > 0:
                self.wait_time -= 1
                self.stay_counter += 1
            elif not self.route:  # calcular ruta si no tiene
                if self.state == None:  # primera vez o acaba de llegar al piso destino
                    if self.locker_room!=None and self.locker_room.floor==self.current_floor:
                        self.target_coords = self.locker_room.getPointInside()
                        self.state = 'moving_lockers'
                    elif (self.target_area.floor != self.current_floor) or (self.locker_room!=None and self.locker_room.floor!=self.current_floor):  # target is not in this floor -> go to stairs
                        self.target_coords = self.stairs[self.current_floor].getPointInside()
                        self.state = 'moving_stairs'
                    else:  # target on this floor -> go to it
                        # if self.target_area == 'PG':
                        self.target_coords = self.target_area.getPointInside(self.id%6)
                        # else:
                        #     self.target_coords = self.target_area.getPointInside()
                        self.state = 'moving_target'
                    # print(self.x, self.y, self.target_coords)
                    # self.route = self.getEasyRoute((int(self.x), int(self.y)), self.target_coords, step=10)
                    # self.route = a_star_search((int(self.x), int(self.y)), self.target_coords, f"Planta{self.current_floor}", padding=0, scale_factor=5)
                                
                    self.route = a_star_search_from_grid(grid=MATRIX_FLOOR[self.current_floor], 
                                                         src=(int(self.x), int(self.y)), dest=self.target_coords,
                                                         scale_factor=SCALE_FACTOR,
                                                         debug=False)
                    self.x, self.y = self.route.pop(0)  # move to next cell in route in any case

                elif self.state == 'moving_stairs': # if stairs, go to lockers or destination floor
                    if self.locker_room != None:
                        self.current_floor = self.locker_room.floor
                    else:
                        self.current_floor = self.target_area.floor
                    # change to spawn on that floor
                    self.x, self.y = self.stairs[self.current_floor].getPointInside()
                    self.state = None
                elif self.state == 'moving_lockers':
                    self.locker_room = None
                    self.state = None
                elif self.state == 'moving_target': # if target, finish
                    self.state = 'reached'
                elif self.state == 'reached':
                    
                    if self.target_area.type == 'PG':
                        self.route = POOL_LANES[self.id%6].copy()
                    else:
                        self.target_coords = self.target_area.getPointInside()
                        self.route = a_star_search_from_grid(grid=MATRIX_FLOOR[self.current_floor], 
                                                         src=(int(self.x), int(self.y)), dest=self.target_coords,
                                                         scale_factor=SCALE_FACTOR,
                                                         debug=False)
                    self.x, self.y = self.route.pop(0)  # move to next cell in route in any case

                    self.stay_counter += 1
                    self.wait_time = random.randint(10, 30)
            else:
                self.x, self.y = self.route.pop(0)
        #print(f"Person {self.id} is ({self.state}, on {self.target_area.name if self.target_area else 'None'}, at {self.x}, {self.y}, floor {self.current_floor})")
        self.history.append((self.x, self.y, self.current_floor, self.state))

