from collections import deque

import numpy as np


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


class Map:
    def __init__(self):
        self._adjacency_matrix = get_map()
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

    def get_edges(self):
        return self._edges
