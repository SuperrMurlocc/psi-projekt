import numpy as np

from psi_environment.data.map import Map
from psi_environment.data.map_state import Road


class EnvironmentAPI:
    def __init__(self, _map: Map):
        self._map = _map

    def get_adjacency_matrix(self) -> np.ndarray:
        """
        Returns the adjacency matrix of the environment's nodes
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        return self._map.get_map_state().get_adjacency_matrix()

    def get_traffic(self) -> np.ndarray:
        """
        Returns the traffic matrix
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        size = self._map.get_map_state().get_adjacency_matrix_size()
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
        size = self._map.get_map_state().get_adjacency_matrix_size()

        if 0 > from_node > size and 0 > to_node > size:
            raise ValueError("Incorrect values of from_node and to_node")

        roads = self._map.get_map_state().get_roads()

        if (from_node, to_node) not in roads.keys():
            return np.nan

        return np.count_nonzero(roads[(from_node, to_node)])

    def get_points_position(self) -> dict[tuple[int, int], Road]:
        """
        Method return the dict representing the all the roads
        :return:
        """
        return self._map.get_map_state().get_roads()
