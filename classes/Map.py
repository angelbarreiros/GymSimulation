import numpy as np
import cv2

class Area:
    def __init__(self, id, points, aforo):
        self.id = id
        self.points = np.array(points, dtype=np.int32)  # Ensure points are numpy array
        self.occupied_by = None
        self.center_x = np.mean(self.points[:, 0])
        self.center_y = np.mean(self.points[:, 1])
        self.aforo = aforo

    def contains_point(self, point_x, point_y):
        #print(f'Checking if point ({point_x}, {point_y}) is inside area {self.id}')
        point = np.array([point_x, point_y], dtype=np.float32)
        return cv2.pointPolygonTest(self.points, point, False) >= 0

class Boundary:
    def __init__(self, points):
        self.points = np.array(points, dtype=np.int32)

    def touchs(self, point_x, point_y):
        return False
    
    
class SpawnPoint:
    def __init__(self, id, points):
        self.id = id
        self.coords = np.array(points, dtype=np.int32)
