import numpy as np
import cv2

class Area:
    def __init__(self, name, points, totalCapacity, targetCapacity, floor, type, machines):
        self.name = name
        self.points = np.array(points, dtype=np.int32)  # Ensure points are numpy array
        self.actualCapacity = 0
        self.totalCapacity = totalCapacity
        self.targetCapacity = targetCapacity
        self.floor = floor
        self.type = type
        self.machines = machines
        # self.ocuppiedMachines = [-1] * len(machines)

    def getPointInside(self, id=None):
        if self.machines:  # If area has machines, choose a random machine that isn't occupied
            if self.type == 'PG':  # If not on the pool yet, choose 1 of the 6 lanes.
               return self.machines[id % 6][0]
            else:
                return self.machines[np.random.randint(0, len(self.machines))][0]
            # elif self.actualCapacity < len(self.machines):
            #     # available_machines = [i for i, occupied in enumerate(self.ocuppiedMachines) if occupied == -1]
            #     # if available_machines:
            #     #     chosen_machine = np.random.choice(available_machines)
            #     #     self.ocuppiedMachines[chosen_machine] = id
            #     #     print(f"Chosen machine: {self.machines[chosen_machine][0]} in {self.name}")
            #     #     return tuple(self.machines[chosen_machine][0])
            #     return self.machines[self.actualCapacity][0]

        x, y, w, h = cv2.boundingRect(self.points)
        margin = 5
        while True:
            random_point = (np.random.randint(x+margin, x + w-margin), np.random.randint(y+margin, y + h-margin))
            if cv2.pointPolygonTest(self.points, random_point, False) >= 0:
                return random_point

    def contains_point(self, point_x, point_y):
        return cv2.pointPolygonTest(self.points, np.array([point_x, point_y], dtype=np.float32), False) >= 0
    def __str__(self):
        return f"Area('{self.name}', {self.points}, {self.targetCapacity}, {self.totalCapacity})"

class Boundary:
    def __init__(self, points, floor):
        self.points = np.array(points, dtype=np.int32)
        self.floor = floor

    def touchs(self, point_x, point_y):
        return False
    
class SpawnPoint:
    def __init__(self, name, points, floor):
        self.name = name
        self.coords = np.array(points, dtype=np.int32)
        self.floor = floor
        self.type = 'SpawnPoint'
    def getPointInside(self, id=None):
        return self.coords

class Activity:
    def __init__(self,name,startDate,endDate,Area):
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.Area = Area