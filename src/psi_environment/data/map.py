from collections import deque
import importlib
import numpy as np


def get_map(filename="sample_map.txt") -> np.ndarray:
    """
    Generates array map of a sample map saved in ./game/resources/sample.map.txt
    :return: map as a numpy array
    """

    with importlib.resources.open_text("psi_environment.game.resources", filename) as f:
        content = f.read()

    map_array = content.split()
    map_array = np.array([[*row] for row in map_array])
    return map_array


def create_adjacency_matrix(content) -> np.ndarray:
    """
    Generates adjacency matrix of a sample map from map numpy array
    :return: adjacency matrix of the map as a numpy array
    """

    node_character = "x"
    connecting_characters = {"=", "|"}
    empty_character = "#"

    node_indices = {}
    index = 0
    for y in range(content.shape[0]):
        for x in range(content.shape[1]):
            if content[y][x] == node_character:
                node_indices[(x, y)] = index
                index += 1

    n_nodes = len(node_indices)

    adjacency_matrix = np.full((n_nodes, n_nodes), np.nan)

    directions = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    for (x, y), node_index in node_indices.items():
        for dx, dy in directions:
            route_length = 1
            while True:
                # try to find next node in a given direction
                nx = x + route_length * dx
                ny = y + route_length * dy
                if nx < 0 or ny < 0 or nx >= content.shape[1] or ny >= content.shape[0]:
                    break
                if content[ny][nx] in {node_character, empty_character}:
                    break
                route_length += 1

            # if we found a node
            if (nx, ny) in node_indices and content[ny][nx] == node_character:
                neighbor_index = node_indices[(nx, ny)]
                # subtract 1 because we don't count the node itself
                adjacency_matrix[node_index, neighbor_index] = route_length - 1

    return adjacency_matrix


class Map:
    def __init__(self):
        self._map_array = get_map()
        self._adjacency_matrix = create_adjacency_matrix(self._map_array)
        self._edges = {}
        for y in range(self._adjacency_matrix.shape[0]):
            for x in range(y, self._adjacency_matrix.shape[1]):
                if self._adjacency_matrix[y, x] != np.nan:
                    self._edges[(y, x)] = deque()
                    self._edges[(x, y)] = deque()

    def get_adjacency_matrix_size(self):
        return self._adjacency_matrix.shape[0]

    def get_adjacency_matrix(self):
        return self._adjacency_matrix

    def get_map_array(self):
        return self._map_array

    def get_edges(self):
        return self._edges
