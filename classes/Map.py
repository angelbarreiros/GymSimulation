import numpy as np
import cv2

class Area:
    def __init__(self, name, points, totalCapacity, targetCapacity):
        self.name = name
        self.points = np.array(points, dtype=np.int32)  # Ensure points are numpy array
        self.actualCapacity = 0
        self.center_x = np.mean(self.points[:, 0])
        self.center_y = np.mean(self.points[:, 1])
        self.totalCapacity = totalCapacity
        self.ocuppied_by = None # quitarrrr
        self.targetCapacity = targetCapacity

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
