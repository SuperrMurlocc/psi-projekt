import importlib

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
    ):
        self.length = length_on_map * cars_per_length
        self._road = np.zeros((self.length,))
        self._front_node = front_node
        self._back_node = back_node
        self._adjacent_nodes = adjacent_nodes

    def get_road(self):
        return self._road

    def get_length(self):
        return self.length

    def __repr__(self) -> str:
        return repr(self._road)


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


def get_node_indices(map_array) -> dict:
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

        self._edges = []
        for x_node in self._node_indices.values():
            for y_node in self._node_indices.values():
                if not np.isnan(self._adjacency_matrix[x_node, y_node]):
                    self._edges.append((x_node, y_node))

        self._roads: dict[tuple[int, int], Road] = {}
        for back_node, front_node in self._edges:
            adjacent_edges = [edge for edge in self._edges if edge[0] == front_node]
            adjacent_nodes = {edge[1] for edge in adjacent_edges} - {back_node}
            length_on_map = int(self._adjacency_matrix[back_node, front_node])
            self._roads[(back_node, front_node)] = Road(
                length_on_map=length_on_map,
                front_node=front_node,
                back_node=back_node,
                adjacent_nodes=adjacent_nodes,
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
