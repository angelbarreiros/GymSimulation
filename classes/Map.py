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
        self.ocuppiedMachines = [False] * len(machines)

    def getPointInside(self):
        if self.machines:  # If area has machines, choose a random machine that isn't occupied
            if self.type == 'PG':
                return self.machines[np.random.randint(6)][0]
            else:
                available_machines = [i for i, occupied in enumerate(self.ocuppiedMachines) if not occupied]
                if available_machines:
                    chosen_machine = np.random.choice(available_machines)
                    self.ocuppiedMachines[chosen_machine] = True
                    #print(f"Area {self.name} has {self.machines[chosen_machine]}")
                    return tuple(self.machines[chosen_machine][0]) 

        x, y, w, h = cv2.boundingRect(self.points)
        while True:
            random_point = (np.random.randint(x, x + w), np.random.randint(y, y + h))
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
