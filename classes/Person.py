import numpy as np

class Person:
    def __init__(self, person_id, start_x, start_y, startFrame, max_step=20):
        self.id = person_id
        self.x = start_x
        self.y = start_y
        self.max_step = max_step
        self.history = [(start_x, start_y)]
        self.stay_counter = 0
        self.target_area = None
        self.last_target_area = None
        self.last_direction = None
        self.scapeCnt = 0
        self.startFrame = startFrame

    def move(self, others, boundary, target_areas):
        if self.stay_counter > 0:
            self.stay_counter -= 1
            if self.stay_counter == 0:
                if self.target_area:
                    self.last_target_area = self.target_area
                    self.target_area.occupied_by = None
                    self.target_area = None
        elif self.target_area:
            self.move_towards_target(others, boundary, target_areas)
        else:
            self.choose_new_target(target_areas)
        
        self.history.append((self.x, self.y))

    def move_towards_target(self, others, boundary, target_areas):
        target_x, target_y = self.target_area.center_x, self.target_area.center_y
        dx = target_x - self.x
        dy = target_y - self.y
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance <= 0.5:
            if self.target_area.occupied_by is not None and self.target_area.occupied_by != self:
                # Target is occupied by someone else, choose a new target
                self.last_target_area = self.target_area
                self.target_area = None
                self.choose_new_target(target_areas)
                return
        
        #print(f'Person {self.id} moving towards target {self.target_area.id}')
        #print(f'Current position: ({self.x}, {self.y})')
        if self.target_area.contains_point(self.x, self.y):
            self.target_area.occupied_by = self
        
        if distance < 0.01:  # If very close to the center, snap to it
            self.x, self.y = target_x, target_y
            self.target_area.occupied_by = self
            self.stay_counter = np.random.randint(5, 26)  # Stay for 5-25 steps
            return

        step = min(self.max_step, distance)
        new_x = self.x + dx * step / distance
        new_y = self.y + dy * step / distance
        
        # Define possible directions
        directions = [
            (self.max_step, 0),
            (0, self.max_step),
            (-self.max_step, 0),
            (0, -self.max_step)    
        ]

        if self.is_valid_move(new_x, new_y, others, boundary, target_areas):
            self.x, self.y = new_x, new_y
            return
        
        # If infinite loop motion, choose new target
        # TODO Scape algorith (target intermediate points)
        # elif self.history[-3] == (self.x, self.y):
        #     self.scapeCnt = 25
        #     return
        
            
        else:
            
            # if self.history[-3] == (self.x, self.y) and self.scapeCnt==0:# and self.history[-2] != (self.x, self.y):
            #     self.lastDirection = (round(abs(self.history[-2][0]-self.x),4), round(abs(self.history[-2][1]-self.y),4))
            #     if self.lastDirection in directions:
            #         self.scapeCnt = 25
                # self.lastDirection = directions.index(self.lastDirection)
                # if self.lastDirection == (0,0):
                #     print('hola')
                # directions = directions[(directions.index(lastDirection)+1)%4]
        
            if self.scapeCnt > 0:
                # new_x, new_y = directions[(directions.index(self.lastDirection))%4]
                new_x, new_y = self.lastDirection
                if self.is_valid_move(new_x, new_y, others, boundary, target_areas):
                    # self.scapeCnt = 2
                    # self.scapeCnt -= 1
                    self.scapeCnt = 0
                    self.x += new_x
                    self.y += new_y
                    return
                else:
                    self.scapeCnt -= 1
                    directions.pop(directions.index(self.lastDirection))
                    
                    # self.lastDirection = (round(abs(self.history[-2][0]-self.x),4), round(abs(self.history[-2][1]-self.y),4))
                    # lastDirectionIdx = directions.index((abs(self.history[-1][0]-self.x), abs(self.history[-1][1]-self.y)))
                    
                    # if self.lastDirection in directions:
                    #     directions.pop((directions.index(self.lastDirection))%4)
                    # else:
                    #     self.scapeCnt = 0
                        # return
            # else:
            #     lastDirection = None
            else:
                # Calculate angle to target
                angle = np.arctan2(dy, dx)
            
                # Sort directions based on closeness to target angle
                directions = sorted(directions, key=lambda d: abs(np.arctan2(d[1], d[0]) - angle))
            
            # if lastDirection == sorted_directions[0]:
            #     self.scapeCnt = 0
            
            for dx, dy in directions:
                new_x = self.x + dx
                new_y = self.y + dy
                if self.is_valid_move(new_x, new_y, others, boundary, target_areas):
                    # if self.id == 8 and len(self.history)>240:
                    #     print(f'A: {self.history[-3]} B:{(self.x, self.y)} C: {self.history[-3]==(self.x, self.y)}')
                    self.x, self.y = new_x, new_y
                    return
        
        self.target_area = None
        
        # self.last_target_area = None
        
    def choose_new_target(self, target_areas):
        available_areas = [a for a in target_areas if a.ocuppied_by is None and a != self.last_target_area]
        if available_areas:
            self.target_area = np.random.choice(available_areas)
            # self.target_area.occupied_by = self

    # def wander_randomly(self, others, boundary, target_areas):
    #     for _ in range(10):  # Try up to 10 times to find a valid move
    #         angle = np.random.uniform(0, 2 * np.pi)
    #         new_x = self.x + self.max_step * np.cos(angle)
    #         new_y = self.y + self.max_step * np.sin(angle)

    #         if self.is_valid_move(new_x, new_y, others, boundary, target_areas):
    #             self.x, self.y = new_x, new_y
    #             return
    #     # If no valid move is found after 10 attempts, stay in place

    def is_valid_move(self, new_x, new_y, others, boundary, target_areas):
        
        #TODO Areas can be crossed; walls and machines can't.
        
        # if not boundary.contains_point((new_x, new_y)):
        #     return False
        
        for other in others:
            if other.id != self.id:
                distance = np.sqrt((new_x - other.x)**2 + (new_y - other.y)**2)
                if distance < 0.1:
                    return False
        
        for area in target_areas:
            if (area != self.target_area and 
            # TODO last_target_area can only be step until person exits it
            # area != self.last_target_area and
            not area.contains_point(self.x, self.y) and
            area.contains_point(new_x, new_y)):
                return False
        
        return True
    