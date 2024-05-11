import random
import numpy as np
from collections import deque


def get_map() -> np.ndarray:
    """
    Generates adjacency matrix of a simple static map
    :return: adjacency matrix of the map as a numpy array
    """
    adjacency_matrix = np.array([
        [0, 1, 0, 0, 1, 0, 0, 0],
        [1, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 1],
        [0, 0, 0, 1, 0, 0, 1, 0],
    ])
    return adjacency_matrix


class Environment:
    def __init__(self, random_seed: int = None):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        self._timestep = 0

        self._map = get_map()

        # Preparing 2-directional queue for each connection between crossroads
        self._edges = {}
        for y in range(self._map.shape[0]):
            for x in range(y, self._map.shape[1]):
                if self._map[y, x] != 0:
                    self._edges[(y, x)] = deque()
                    self._edges[(x, y)] = deque()
