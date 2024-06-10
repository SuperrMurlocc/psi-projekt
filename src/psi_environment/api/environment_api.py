import numpy as np

from psi_environment.data.map_state import MapState


class EnvironmentAPI:
    def __init__(self, map_state: MapState):
        self._map_state = map_state

    def get_adjacency_matrix(self):
        """
        Returns the adjacency matrix of the environment's nodes
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        return self._map_state.get_adjacency_matrix()

    def get_traffic(self):
        """
        Returns the traffic matrix
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        size = self._map_state.get_adjacency_matrix_size()
        traffic_matrix = np.full((size, size), np.nan)

        for i in range(size):
            for j in range(size):
                traffic_matrix[i, j] = self.get_specific_traffic(i, j)
        return traffic_matrix

    def get_specific_traffic(self, from_node: int, to_node: int):
        """
        :param from_node: integer representing the index of start node
        :param to_node: integer representing the index of end node
        :return: integer represents traffic from node to node
        """
        size = self._map_state.get_adjacency_matrix_size()

        if 0 > from_node > size and 0 > to_node > size:
            raise ValueError("Incorrect values of from_node and to_node")

        roads = self._map_state.get_roads()

        if (from_node, to_node) not in roads.keys():
            return np.nan

        return np.count_nonzero(roads[(from_node, to_node)])

    def is_position_road_end(self, road_key: tuple[int, int], pos_idx: int) -> bool:
        road = self._map_state.get_road(road_key)
        return pos_idx == road.length - 1
