import numpy as np

class SpawnPoint:
    def __init__(self, id, points):
        self.id = id
        self.coords = np.array(points, dtype=np.int32)
