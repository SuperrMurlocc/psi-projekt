import numpy as np

from psi_environment.data.map_state import MapState
from psi_environment.data.action import Action


class EnvironmentAPI:
    """Defines the API for interacting with the environment, including functions for getting data about cost, map state, and traffic.
    """
    def __init__(self, map_state: MapState):
        self._map_state = map_state

    def get_adjacency_matrix(self) -> np.ndarray:
        """Returns the adjacency matrix representing the connections between nodes in the map.

        Returns:
            np.ndarray: The adjacency matrix of the map
        """
        return self._map_state.get_adjacency_matrix()

    def get_traffic(self) -> np.ndarray:
        """Returns the traffic matrix, indicating the number of cars between nodes.

        Returns:
            np.ndarray: A matrix with shape (num_nodes, num_nodes), where each element represents the traffic from one node to another.
        """
        size = self._map_state.get_adjacency_matrix_size()
        traffic_matrix = np.full((size, size), np.nan)

        for i in range(size):
            for j in range(size):map status
                traffic_matrix[i, j] = self.get_specific_traffic(i, j)
        return traffic_matrix

    def get_specific_traffic(self, from_node: int, to_node: int) -> int:
        """Returns the traffic from a specific node to another

        Args:
            from_node (int): The index of the start node.
            to_node (int): The index of the end node

        Raises:
            ValueError: If the from_node or to_node values are incorrect.

        Returns:
            int: The number of cars from the start node to the end node.
        """
        size = self._map_state.get_adjacency_matrix_size()

        if 0 > from_node > size and 0 > to_node > size:
            raise ValueError("Incorrect values of from_node and to_node")

        roads = self._map_state.get_roads()

        if (from_node, to_node) not in roads.keys():
            return np.nan

        return roads[(from_node, to_node)].get_number_of_cars()

    def is_position_road_end(self, road_key: tuple[int, int], pos_idx: int) -> bool:
        """Checks if a given position index is at the end of a road.

        Args:
            road_key (tuple[int, int]): The key identifying the road.
            pos_idx (int): The position index to check.

        Returns:
            bool: True if the position is at the end of the road, False otherwise
        """
        road = self._map_state.get_road(road_key)
        return road.is_position_road_end(pos_idx)

    def get_available_turns(self, road_key: tuple[int, int]) -> list[Action]:
        """Returns a list of available actions at a given road.

        Args:
            road_key (tuple[int, int]): The key identifying the road.

        Returns:
            list[Action]: A list of available actions at the specified road.
        """
        road = self._map_state.get_road(road_key)
        return road.get_available_turns()
