import numpy as np

class Boundary:
    def __init__(self, points):
        self.points = np.array(points, dtype=np.int32)

    def touchs(self, point_x, point_y):
        return False
