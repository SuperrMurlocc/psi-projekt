import numpy as np

from src.psi_environment.environment import Environment


class EnvironmentAPI:
    def __init__(self, environment: Environment):
        self.environment = environment

    def get_adjacency_matrix(self):
        """
        Returns the adjacency matrix of the environment's nodes
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        return self.environment.get_map()

    def get_traffic(self):
        """
        Returns the traffic matrix
        :return: numpy array with shape (num_nodes, num_nodes)
        """
        size = self.environment.get_map_size()
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
        size = self.environment.get_map_size()

        if 0 > from_node > size and 0 > to_node > size:
            raise ValueError("Incorrect values of from_node and to_node")

        edges = self.environment.get_edges()

        if (from_node, to_node) not in edges.keys():
            return np.nan

        return len(edges[(from_node, to_node)])
