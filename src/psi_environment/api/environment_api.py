import numpy as np

from psi_environment.data.map_state import MapState, Road
from psi_environment.data.action import Action


class EnvironmentAPI:
    """Defines the API for interacting with the environment, including functions for
    getting data about cost, map state, and traffic."""

    def __init__(self, map_state: MapState):
        self._map_state = map_state

    def get_adjacency_matrix(self) -> np.ndarray:
        """Returns the adjacency matrix representing the connections between nodes in
        the map.

        Returns:
            np.ndarray: The adjacency matrix of the map
        """
        return self._map_state.get_adjacency_matrix()

    def get_road(self, road_key: tuple[int, int]) -> Road | None:
        """Returns the road with the given key or None if it doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            Road | None: The road with the given key or None if it doesn't exist
        """
        return self._map_state.get_road(road_key)

    def get_road_length(self, road_key: tuple[int, int]) -> int:
        """Returns the length of the road with the given key or np.nan if it doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            int: The length of the road with the given key or np.nan if it doesn't exist
        """
        road = self._map_state.get_road(road_key)
        if road is None:
            return np.nan
        return road.get_length()

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

    def get_next_road(self, road_key: tuple[int, int], action: Action) -> Road | None:
        """Returns the road that follows the road with the given key in given direction
        or None if it doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road
            action (Action): The action to take from the road

        Returns:
            Road | None: The forward road from the road with the given key or None if
                it doesn't exist
        """
        road = self._map_state.get_road(road_key)
        if road is None:
            return None

        if action == Action.RIGHT:
            next_road_key = road.get_right_road_key()
        elif action == Action.LEFT:
            next_road_key = road.get_left_road_key()
        elif action == Action.FORWARD:
            next_road_key = road.get_forward_road_key()
        elif action == Action.BACK:
            next_road_key = road.get_backward_road_key()

        if next_road_key is None:
            return None
        return self._map_state.get_road(next_road_key)

    def get_forward_road(self, road_key: tuple[int, int]) -> Road | None:
        """Returns the forward road from the road with the given key or None if it
        doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            Road | None: The forward road from the road with the given key or None if
                it doesn't exist
        """
        return self.get_next_road(road_key, Action.FORWARD)

    def get_backward_road(self, road_key: tuple[int, int]) -> Road | None:
        """Returns the backward road from the road with the given key or None if it
        doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            Road | None: The backward road from the road with the given key or None if
                it doesn't exist
        """
        return self.get_next_road(road_key, Action.BACK)

    def get_left_road(self, road_key: tuple[int, int]) -> Road | None:
        """Returns the left road from the road with the given key or None if it
        doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            Road | None: The left road from the road with the given key or None if
                it doesn't exist
        """
        return self.get_next_road(road_key, Action.LEFT)

    def get_right_road(self, road_key: tuple[int, int]) -> Road | None:
        """Returns the right road from the road with the given key or None if it
        doesn't exist.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            Road | None: The right road from the road with the given key or None if
                it doesn't exist
        """
        return self.get_next_road(road_key, Action.RIGHT)

    def get_road_traffic(self, road_key: tuple[int, int]) -> int:
        """Returns the number of cars on the road with the given key.

        Args:
            road_key (tuple[int, int]): The key of the road

        Returns:
            int: The number of cars on the road with the given key
        """
        road = self._map_state.get_road(road_key)
        if road is None:
            return np.nan

        return road.get_number_of_cars()

    def get_specific_traffic(self, from_node: int, to_node: int) -> int:
        """Returns the traffic from a specific node to another, indicating the number of
        cars between nodes. Acts like get_road_traffic(), but receives node indices as
        seperate arguments instead of a tuple.

        Args:
            from_node (int): The index of the start node.
            to_node (int): The index of the end node

        Returns:
            int: The number of cars from the start node to the end node.
        """
        self.get_road_traffic((from_node, to_node))

    def get_traffic(self) -> np.ndarray:
        """Returns the traffic matrix, indicating the number of cars between nodes.

        Returns:
            np.ndarray: A matrix with shape (num_nodes, num_nodes), where each element
                is an integer that represents the number of cars from one node to
                another.
        """
        size = self._map_state.get_adjacency_matrix_size()
        traffic_matrix = np.full((size, size), np.nan)

        for i in range(size):
            for j in range(size):
                traffic_matrix[i, j] = self.get_specific_traffic(i, j)
        return traffic_matrix

    def get_points_positions(self) -> list[tuple[int, int]]:
        """Returns a list of the positions of the points on the map.

        Returns:
            list[tuple[int, int]]: A list of the positions of the points on the map.
        """
        points = self._map_state.get_points()
        return list(points.values())

    def get_cars_positions(
        self, car_id_to_ignore: int | None = None
    ) -> list[tuple[tuple[int, int], int]]:
        """Returns a list of the positions of the cars on the map.

        Args:
            car_id_to_ignore (int, optional): The ID of the car to ignore.
                Defaults to None.

        Returns:
            list[tuple[tuple[int, int], int]]: A list of the positions of the cars on the map.
        """
        cars = self._map_state.get_cars()

        cars_positions = [
            car_position for car_id, car_position in cars if car_id != car_id_to_ignore
        ]

        return cars_positions

    def get_available_turns(self, road_key: tuple[int, int]) -> list[Action]:
        """Returns a list of available actions at a given road.

        Args:
            road_key (tuple[int, int]): The key identifying the road.

        Returns:
            list[Action]: A list of available actions at the specified road.
        """
        road = self._map_state.get_road(road_key)

        if road is None:
            return []

        return road.get_available_turns()
