import importlib
from enum import IntEnum

import numpy as np

from psi_environment.data.action import Action

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
        front_indicies: tuple[int, int],
        back_node: int,
        back_indicies: tuple[int, int],
        adjacent_nodes: set,
        cars_per_length: int = 2,
        left_node: int = None,
        right_node: int = None,
        forward_node: int = None,
    ):
        self.length = length_on_map * cars_per_length
        self._cars_per_length = cars_per_length
        self._road = np.zeros((self.length,))
        self._front_node = front_node
        self._front_indicies = front_indicies
        self._back_node = back_node
        self._back_indicies = back_indicies
        self._adjacent_nodes = adjacent_nodes
        self._left_node = left_node
        self._right_node = right_node
        self._forward_node = forward_node

    def get_road(self):
        return self._road

    def get_length(self):
        return self.length

    def get_inverted_position(self, pos: int) -> int:
        return self.length - 1 - pos

    def __repr__(self) -> str:
        return repr(self._road)

    def __getitem__(self, idx: int):
        return self._road[idx]

    def __setitem__(self, idx, value):
        self._road[idx] = value

    def __delitem__(self, idx: int):
        self._road[idx] = 0

    def get_key(self):
        return (self._back_node, self._front_node)

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

    def get_number_of_cars(self) -> int:
        return np.count_nonzero(self._road)

    def get_map_position(self, pos: int) -> tuple[int, int]:
        if pos < 0 or pos >= self.length:
            raise ValueError("Position out of range")
        relative_pos = 1 + pos // self._cars_per_length
        front_indices = np.array(self._front_indicies)
        back_indices = np.array(self._back_indicies)
        diff = back_indices - front_indices
        diff = np.where(diff != 0, relative_pos * np.sign(diff), 0)
        return tuple(back_indices - diff)


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


def get_node_indices(map_array) -> dict[int, tuple[int, int]]:
    """
    Finds node indices of a sample map
    :return: node indices of the map as a dictionary
    """

    node_indices = {}
    index = 0
    for y in range(map_array.shape[0]):
        for x in range(map_array.shape[1]):
            if map_array[y][x] == NODE_CHARACTER:
                node_indices[index] = (x, y)
                index += 1
    return node_indices


def create_adjacency_matrix(
    content: np.ndarray, node_indices: dict[int, tuple[int, int]]
) -> np.ndarray:
    """
    Generates adjacency matrix of a sample map from map numpy array
    :return: adjacency matrix of the map as a numpy array
    """

    n_nodes = len(node_indices)
    indices_node = {v: k for k, v in node_indices.items()}

    adjacency_matrix = np.full((n_nodes, n_nodes), np.nan)

    directions = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    for node_index, (x, y) in node_indices.items():
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
            if (nx, ny) in indices_node and content[ny][nx] == NODE_CHARACTER:
                neighbor_index = indices_node[(nx, ny)]
                # subtract 1 because we don't count the node itself
                adjacency_matrix[node_index, neighbor_index] = route_length - 1

    return adjacency_matrix


def create_edges(
    node_indices: dict[int, tuple[int, int]], adjacency_matrix: np.ndarray
) -> dict[tuple[int, int], Direction]:
    edges = {}
    for x_index, (x_x, x_y) in node_indices.items():
        for y_index, (y_x, y_y) in node_indices.items():
            if not np.isnan(adjacency_matrix[x_index, y_index]):
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

                edges[(x_index, y_index)] = direction
    return edges


def create_roads(
    edges: dict[tuple[int, int], Direction],
    adjacency_matrix: np.ndarray,
    node_indices: dict[int, tuple[int, int]],
) -> dict[tuple[int, int], Road]:
    roads = {}
    for back_node, front_node in edges.keys():
        adjacent_edges = [edge for edge in edges.keys() if edge[0] == front_node]
        adjacent_nodes = {edge[1] for edge in adjacent_edges} - {back_node}
        length_on_map = int(adjacency_matrix[back_node, front_node])

        left_node = None
        right_node = None
        forward_node = None
        road_direction = edges[(back_node, front_node)]
        for adjacent_node in adjacent_nodes:
            node_direction = edges[(front_node, adjacent_node)]
            relative_direction = road_direction.relative_direction(node_direction)

            if relative_direction == Direction.LEFT:
                left_node = adjacent_node
            elif relative_direction == Direction.RIGHT:
                right_node = adjacent_node
            elif relative_direction == Direction.UP:
                forward_node = adjacent_node

        roads[(back_node, front_node)] = Road(
            length_on_map=length_on_map,
            front_node=front_node,
            front_indicies=node_indices[front_node],
            back_node=back_node,
            back_indicies=node_indices[back_node],
            adjacent_nodes=adjacent_nodes,
            left_node=left_node,
            right_node=right_node,
            forward_node=forward_node,
        )
    return roads


class MapState:
    def __init__(self, random_seed: int):
        self._random_seed = random_seed
        self._map_array = get_map()
        self._node_indices = get_node_indices(self._map_array)
        self._adjacency_matrix = create_adjacency_matrix(
            self._map_array, self._node_indices
        )
        self._edges = create_edges(self._node_indices, self._adjacency_matrix)
        self._roads = create_roads(
            self._edges, self._adjacency_matrix, self._node_indices
        )
        self._cars = {}
        self._points = {}

    def _add_car(self, road_key: tuple[int, int], car_id) -> int:
        road = self._roads[road_key]
        pos_idx = np.random.randint(road.length)
        road.get_road()[pos_idx] = car_id
        self._cars[car_id] = (road_key, pos_idx)

    def add_cars(self, n: int) -> dict[int, tuple[tuple[int, int], int]]:
        # TODO: breaks if number of cars is greater than number of roads
        if n > len(self._roads):
            raise ValueError("Number of cars is greater than number of roads")

        road_idxs = np.random.choice(len(self._roads), size=n, replace=False)
        road_keys = [list(self._roads)[idx] for idx in road_idxs]

        for i, road_key in enumerate(road_keys):
            car_idx = i + 1
            self._add_car(road_key, car_idx)

        return self._cars

    def add_points(self, n: int) -> dict[int, tuple[tuple[int, int]]]:
        road_tile_positions = self.get_road_tiles_map_positions()
        road_tile_idxs = np.random.choice(
            len(road_tile_positions), size=n, replace=False
        )

        for i, road_tile_idx in enumerate(road_tile_idxs):
            point_id = i + 1
            point_position = road_tile_positions[road_tile_idx]
            self._points[point_id] = point_position

        return self._points

    def move_car(self, car_id: int, action: Action, collect_point: bool = False):
        car_road_key = self._cars[car_id][0]
        car_road_pos = self._cars[car_id][1]

        current_road = self.get_road(car_road_key)
        if action == Action.BACK:
            inv_road_key = current_road.get_backward_road_key()
            next_road = self.get_road(inv_road_key)
            inv_pos = current_road.get_inverted_position(car_road_pos)

            if next_road[inv_pos] == 0:
                return self._move_car(car_id, next_road, inv_pos, collect_point)
            return False, car_road_key, car_road_pos

        # Car is not at the end of the road
        if current_road[-1] != car_id:
            if action == Action.FORWARD:
                next_pos = car_road_pos + 1
                if current_road[next_pos] == 0:
                    return self._move_car(car_id, current_road, next_pos, collect_point)
            return False, car_road_key, car_road_pos

        # Car is at the end of the road
        next_road_key = None
        if action == Action.LEFT:
            next_road_key = current_road.get_left_road_key()
        elif action == Action.RIGHT:
            next_road_key = current_road.get_right_road_key()
        elif action == Action.FORWARD:
            next_road_key = current_road.get_forward_road_key()
        next_road = self.get_road(next_road_key) if next_road_key else None
        if next_road and next_road[0] == 0:
            next_pos = 0
            return self._move_car(car_id, next_road, next_pos, collect_point)
        return False, car_road_key, car_road_pos

    def _move_car(self, car_id: int, road: Road, road_pos: int, collect_point: bool):
        car_road_key = self._cars[car_id][0]
        car_road_pos = self._cars[car_id][1]

        current_road = self.get_road(car_road_key)
        current_road[car_road_pos] = 0
        road[road_pos] = car_id
        self._cars[car_id] = (road.get_key(), road_pos)
        if collect_point:
            self._update_collected_points(car_road_key, car_road_pos)
        return True, road.get_key(), road_pos

    def _update_collected_points(self, road_key: tuple[int, int], road_pos: int):
        car_map_position = self.get_road_position_map_position(road_key, road_pos)
        for id, point_position in self._points.items():
            if point_position == car_map_position:
                self._points.pop(id)
                break

    def get_road_tiles_map_positions(self) -> list[tuple[int, int]]:
        road_tiles = []
        for y in range(self._map_array.shape[0]):
            for x in range(self._map_array.shape[1]):
                if self._map_array[y][x] in ROAD_CHARACTERS:
                    road_tiles.append((x, y))
        return road_tiles

    def get_adjacency_matrix_size(self):
        return self._adjacency_matrix.shape[0]

    def get_adjacency_matrix(self):
        return self._adjacency_matrix

    def get_map_array(self):
        return self._map_array

    def get_roads(self):
        return self._roads

    def get_road(self, key: tuple[int, int]):
        return self._roads[key]
    
    def get_cars(self):
        return self._cars
    
    def get_points(self):
        return self._points

    def get_node_map_position(self, node_index: int):
        return self._node_indices[node_index]

    def get_road_position_map_position(self, road_key: tuple[int, int], road_pos: int):
        return self._roads[road_key].get_map_position(road_pos)
