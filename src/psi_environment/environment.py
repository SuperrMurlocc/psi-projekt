import random
from typing import Any

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

    def step(self, action) -> tuple[Any, float, bool]:
        """
        Accepts action provided by agent when has to decide where to go. After that environment continues simulation
        and returns another observation of the environment and cost it took by taking the action.
        :param action: direction where agent wants to go
        :return: tuple of environment observation, cost of this action and bool stating if the agent has finished
        """
        # TODO: This requires a focus if only this will be returned.
        #  Also I'm not sure about how observation will look like.
        #  And the implementation of it has not started
        raise NotImplementedError
