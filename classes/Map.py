import numpy as np
import cv2

class Area:
    def __init__(self, name, points, totalCapacity, targetCapacity):
        self.name = name
        self.points = np.array(points, dtype=np.int32)  # Ensure points are numpy array
        self.actualCapacity = 0
        self.totalCapacity = totalCapacity
        self.targetCapacity = targetCapacity

    def getPointInside(self):
        x, y, w, h = cv2.boundingRect(self.points)
        while True:
            random_point = (np.random.randint(x, x + w), np.random.randint(y, y + h))
            if cv2.pointPolygonTest(self.points, random_point, False) >= 0:
                return random_point
    
    def contains_point(self, point_x, point_y):
        #print(f'Checking if point ({point_x}, {point_y}) is inside area {self.id}')
        return cv2.pointPolygonTest(self.points, np.array([point_x, point_y], dtype=np.float32), False) >= 0
    def __str__(self):
        return f"Area('{self.name}', {self.points}, {self.targetCapacity}, {self.totalCapacity})"

class Boundary:
    def __init__(self, points):
        self.points = np.array(points, dtype=np.int32)

    def touchs(self, point_x, point_y):
        return False
    
    
class SpawnPoint:
    def __init__(self, name, points):
        self.name = name
        self.coords = np.array(points, dtype=np.int32)
