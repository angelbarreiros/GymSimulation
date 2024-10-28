import numpy as np
from utils.shortest_path import create_matrix_from_json, get_easy_route, variable_a_star_search_from_grid
from utils.fixed_route import join_coordinates
import random
from typing import Tuple, List, Optional, Any

# Pre-calculate constants
SCALE_FACTOR = 10
MATRIX_FLOOR = [create_matrix_from_json(floor, SCALE_FACTOR, 1) for floor in range(4)]

LANE_POINTS = [
    [[1386,440],[753,440],[753,470],[1386,470]],
    [[1386,388],[753,388],[753,418],[1386,418]],
    [[1386,336],[753,336],[753,366],[1386,366]],
    [[1386,284],[753,284],[753,314],[1386,314]],
    [[1386,232],[753,232],[753,262],[1386,262]],
    [[1386,180],[753,180],[753,210],[1386,210]]
]
POOL_LANES = [join_coordinates(LANE_POINTS[i], max_step=(i)*3+1) for i in range(len(LANE_POINTS))]

class Person:
    __slots__ = ('id', 'x', 'y', 'current_floor', 'max_step', 'locker_room', 
                 'history', 'stay_counter', 'wait_time', 'target_area', 
                 'startFrame', 'target_coords', 'route', 'stairs', 'state', 
                 'speed', 'lifetime', 'max_lifetime', '_lane_index')
    
    def __init__(self, person_id: int, start_x: float, start_y: float, 
                 startFrame: int, stairs: Any, max_step: int = 20, 
                 target_area: Any = None, floor: int = 0, 
                 locker_room: Any = None, max_lifetime: int = 1000) -> None:
        """Initialize Person with optimized attributes and type hints."""
        self.id = person_id
        self.x = float(start_x)  # Ensure float type
        self.y = float(start_y)
        self.current_floor = floor
        self.max_step = max_step
        self.locker_room = locker_room
        self.history = [(start_x, start_y, floor, None, None)]
        self.stay_counter = 0
        self.wait_time = 0
        self.target_area = target_area
        self.startFrame = startFrame
        self.target_coords = None
        self.route = []
        self.stairs = stairs
        self.state = None
        self.speed = random.randint(20, 40)
        self.lifetime = 0
        self.max_lifetime = max_lifetime
        self._lane_index = person_id % 6  # Cache lane index calculation
        
    @staticmethod
    def _calculate_route(start: Tuple[int, int], end: Tuple[int, int], 
                        step: int) -> List[Tuple[int, int]]:
        """Optimized route calculation using numpy operations."""
        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0
        distance = np.hypot(dx, dy)  # Faster than sqrt(dx**2 + dy**2)
        n_steps = int(distance / step)
        
        if n_steps == 0:
            return [(x1, y1)]
            
        # Vectorized calculation instead of list comprehension
        steps = np.arange(1, n_steps + 1)
        x_coords = x0 + (dx * steps / n_steps)
        y_coords = y0 + (dy * steps / n_steps)
        
        return list(zip(x_coords.astype(int), y_coords.astype(int)))

    def _handle_initial_state(self) -> None:
        """Handle initial state logic."""
        if self.locker_room is not None and self.locker_room.floor == self.current_floor:
            self.target_coords = self.locker_room.getPointInside()
            self.state = 'moving_lockers'
        elif (self.target_area.floor != self.current_floor or 
              (self.locker_room is not None and self.locker_room.floor != self.current_floor)):
            self.target_coords = self.stairs[self.current_floor].getPointInside()
            self.state = 'moving_stairs'
        else:
            self.target_coords = self.target_area.getPointInside(self._lane_index)
            self.state = 'moving_target'

        self.route = variable_a_star_search_from_grid(
            MATRIX_FLOOR[self.current_floor],
            start=(int(self.x), int(self.y)),
            goal=self.target_coords,
            scale_factor=SCALE_FACTOR,
            debug=False,
            speed=self.speed,
            noise_factor=0.2
        )
        
        if self.route is None:
            self.state = None
        else:
            self.x, self.y = self.route.pop(0)

    def _handle_reached_state(self) -> None:
        """Handle reached state logic."""
        if self.target_area.type == 'PG':
            self.wait_time = 10
            self.route = POOL_LANES[self._lane_index].copy()
        elif self.target_area.name in {'EntradaParking', 'EntradaInicial'}:
            self.state = 'left'
            self.target_area = None
            self.current_floor = 0
            self.x = 1750
            self.y = 165 + self.id * 10
            return
        elif self.target_area.floor !=3:
            self.wait_time = random.randint(100, 200)
            self.target_coords = self.target_area.getPointInside(self._lane_index)
            self.route = get_easy_route(
                start=(int(self.x), int(self.y)),
                end=self.target_coords,
                step=self.speed
            )
        else:
            return

        self.x, self.y = self.route.pop(0)
        self.stay_counter += 1

    def move(self) -> None:
        """Optimized move method with state machine pattern."""
        if not (self.target_area and self.state != 'left'):
            self.history.append((self.x, self.y, self.current_floor, self.state, 
                               self.target_area.name if self.target_area else None))
            return

        if self.wait_time > 0:
            self.wait_time -= 1
            self.stay_counter += 1
        elif not self.route:
            if self.state is None:
                self._handle_initial_state()
            elif self.state == 'moving_stairs':
                self.current_floor = (self.locker_room.floor if self.locker_room is not None 
                                    else self.target_area.floor)
                self.x, self.y = self.stairs[self.current_floor].getPointInside()
                self.state = None
            elif self.state == 'moving_lockers':
                self.wait_time = random.randint(50, 100)
                self.locker_room = None
                self.state = None
            elif self.state == 'moving_target':
                self.state = 'reached'
            elif self.state == 'reached':
                self._handle_reached_state()
        else:
            self.x, self.y = self.route.pop(0)

        self.history.append((self.x, self.y, self.current_floor, self.state, 
                           self.target_area.name if self.target_area else None))