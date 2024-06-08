import importlib
from enum import IntEnum

import numpy as np

NODE_CHARACTER = "x"
EMPTY_CHARACTER = "#"
H_ROAD_CHARACTER = "="
V_ROAD_CHARACTER = "|"
ROAD_CHARACTERS = {H_ROAD_CHARACTER, V_ROAD_CHARACTER}


class Road:
    def __init__(
        self,
        length_on_map: int,
        front_node: int,
        back_node: int,
        adjacent_nodes: set,
        cars_per_length: int = 2,
        left_node: int = None,
        right_node: int = None,
        forward_node: int = None,
    ):
        self.length = length_on_map * cars_per_length
        self._road = np.zeros((self.length,))
        self._front_node = front_node
        self._back_node = back_node
        self._adjacent_nodes = adjacent_nodes
        self._left_node = left_node
        self._right_node = right_node
        self._forward_node = forward_node

    def get_road(self):
        return self._road

    def get_length(self):
        return self.length

    def __repr__(self) -> str:
        return repr(self._road)

    def __getitem__(self, idx: int):
        return self._road[idx]

    def __setitem__(self, idx, value):
        self._road[idx] = value

    def __delitem__(self, idx: int):
        self._road[idx] = 0

    def get_left_road_key(self):
        if self._left_node:
            return self._front_node, self._left_node
        return None

    def get_right_road_key(self):
        if self._right_node:
            return self._front_node, self._right_node
        return None

    def get_forward_road_key(self):
        if self._forward_node:
            return self._front_node, self._forward_node
        return None

    def get_backward_road_key(self):
        return self._front_node, self._back_node


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def relative_direction(self, other: "Direction") -> "Direction":
        return Direction((other - self + 4) % 4)


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


def get_node_indices(map_array) -> dict[tuple[int, int], int]:
    """
    Finds node indices of a sample map
    :return: node indices of the map as a dictionary
    """

    node_indices = {}
    index = 0
    for y in range(map_array.shape[0]):
        for x in range(map_array.shape[1]):
            if map_array[y][x] == NODE_CHARACTER:
                node_indices[(x, y)] = index
                index += 1
    return node_indices


def create_adjacency_matrix(content, node_indices) -> np.ndarray:
    """
    Generates adjacency matrix of a sample map from map numpy array
    :return: adjacency matrix of the map as a numpy array
    """

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
                if content[ny][nx] in {NODE_CHARACTER, EMPTY_CHARACTER}:
                    break
                route_length += 1

            # if we found a node
            if (nx, ny) in node_indices and content[ny][nx] == NODE_CHARACTER:
                neighbor_index = node_indices[(nx, ny)]
                # subtract 1 because we don't count the node itself
                adjacency_matrix[node_index, neighbor_index] = route_length - 1

    return adjacency_matrix


class MapState:
    def __init__(self, random_seed: int):
        self._random_seed = random_seed
        self._map_array = get_map()
        self._node_indices = get_node_indices(self._map_array)
        self._adjacency_matrix = create_adjacency_matrix(
            self._map_array, self._node_indices
        )

        self._edges: dict[tuple[int, int], Direction] = {}
        for (x_x, x_y), x_index in self._node_indices.items():
            for (y_x, y_y), y_index in self._node_indices.items():
                if not np.isnan(self._adjacency_matrix[x_index, y_index]):
                    x_pos = np.array([x_x, x_y])
                    y_pos = np.array([y_x, y_y])
                    diff = y_pos - x_pos
                    direction = None
                    if diff[0] > 0:
                        direction = Direction.RIGHT
                    elif diff[0] < 0:
                        direction = Direction.LEFT
                    elif diff[1] > 0:
                        direction = Direction.DOWN
                    elif diff[1] < 0:
                        direction = Direction.UP

                    self._edges[(x_index, y_index)] = direction

        self._roads: dict[tuple[int, int], Road] = {}
        for back_node, front_node in self._edges.keys():
            adjacent_edges = [
                edge for edge in self._edges.keys() if edge[0] == front_node
            ]
            adjacent_nodes = {edge[1] for edge in adjacent_edges} - {back_node}
            length_on_map = int(self._adjacency_matrix[back_node, front_node])

            left_node = None
            right_node = None
            forward_node = None
            road_direction = self._edges[(back_node, front_node)]
            for adjacent_node in adjacent_nodes:
                node_direction = self._edges[(front_node, adjacent_node)]
                relative_direction = road_direction.relative_direction(node_direction)

                if relative_direction == Direction.LEFT:
                    left_node = adjacent_node
                elif relative_direction == Direction.RIGHT:
                    right_node = adjacent_node
                elif relative_direction == Direction.UP:
                    forward_node = adjacent_node

            self._roads[(back_node, front_node)] = Road(
                length_on_map=length_on_map,
                front_node=front_node,
                back_node=back_node,
                adjacent_nodes=adjacent_nodes,
                left_node=left_node,
                right_node=right_node,
                forward_node=forward_node,
            )

    def add_car(self, road_key: tuple[int, int], car_id) -> int:
        road = self._roads[road_key]
        pos_idx = np.random.randint(road.length)
        road.get_road()[pos_idx] = car_id
        return pos_idx

    def get_adjacency_matrix_size(self):
        return self._adjacency_matrix.shape[0]

    def get_adjacency_matrix(self):
        return self._adjacency_matrix

    def get_map_array(self):
        return self._map_array

    def get_roads(self):
        return self._roads

    def get_road(self, key):
        return self._roads[key]
