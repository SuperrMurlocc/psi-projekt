import random
from typing import Any

import numpy as np
from collections import deque

from psi_environment.game.game import Game


def get_map(filename="./game/resources/sample_map.txt") -> np.ndarray:
    """
    Generates adjacency matrix of a sample map saved in ./game/resources/sample.map.txt
    :return: adjacency matrix of the map as a numpy array
    """
    with open(filename) as f:
        content = f.read()

    content = content.split()
    connecting_characters = {"=", "x"}
    content = np.array([[*row] for row in content])

    node_indices = {}
    index = 0
    for y in range(content.shape[0]):
        for x in range(content.shape[1]):
            if content[y][x] in connecting_characters:
                node_indices[(x, y)] = index
                index += 1

    n_nodes = len(node_indices)

    adjacency_matrix = np.full((n_nodes, n_nodes), np.nan)

    moves = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    for (x, y), node_index in node_indices.items():
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in node_indices and content[ny][nx] in connecting_characters:
                neighbor_index = node_indices[(nx, ny)]
                adjacency_matrix[node_index, neighbor_index] = 1

    return adjacency_matrix


class Environment:
    def __init__(self, random_seed: int = None):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        self._map = get_map()
        self._game = Game(self._map, random_seed=random_seed)
        self._is_running = True
        # Preparing 2-directional queue for each connection between crossroads
        self._edges = {}
        for y in range(self._map.shape[0]):
            for x in range(y, self._map.shape[1]):
                if self._map[y, x] != np.nan:
                    self._edges[(y, x)] = deque()
                    self._edges[(x, y)] = deque()

    def step(self, action: int) -> tuple[Any, float, bool]:
        """
        Accepts action provided by agent when has to decide where to go. After that environment continues simulation
        and returns another observation of the environment and cost it took by taking the action.
        :param action: an integer (in range from 0 to 2) of direction where the agent wants to go.
        :return: tuple of environment observation, cost of this action and bool stating if the agent has finished
        """
        # TODO: This requires a focus if only this will be returned.
        #  Also I'm not sure about how observation will look like.
        #  How will be direction handled so it will be consistent. I suggest something like a clock
        #  but it will require some extra checks of edges.
        #  And the implementation of it has not started
        return self._game.step(action)

    def get_timestep(self) -> int:
        """
        Returns timestep of the environment
        :return: timestep of the environment
        """
        return self._game.get_timestep()

    def reset(self):
        """
        Resets environment to the initial state
        """
        return self._game.reset()

    def get_map_size(self):
        return self._map.shape[0]

    def get_map(self):
        return self._map

    def get_edges(self):
        return self._edges
    
    def is_running(self):
        self._is_running = self._game.is_running()
        return self._is_running


class DummyAgent:
    def __init__(self, parent_env: Environment, position: tuple[int, int], random_seed: int):
        """
        :param parent_env: environment in which this agent is placed (may be useful to get current timestep)
        :param position: y, x coordinates of a dummy agent position
        :param random_seed: seed that will be used to take actions
        """
        self._parent_env = parent_env
        self._position = position
        self._random_seed = random_seed

    def get_action(self) -> int:
        return (self._random_seed + self._parent_env.get_timestep()) % 3
