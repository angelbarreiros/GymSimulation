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

    def getPointInside(self):
        # random point
        # x, y, w, h = cv2.boundingRect(self.points)
        # while True:
        #     random_point = (np.random.randint(x, x + w), np.random.randint(y, y + h))
        #     if cv2.pointPolygonTest(self.points, random_point, False) >= 0:
        #         return random_point
        #random machine point  
        return np.random.choice(self.machines)

    
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
