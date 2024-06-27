from typing_extensions import deprecated

import numpy as np

from psi_environment.data.map_state import MapState, Road
from psi_environment.data.action import Action
from psi_environment.data.point import Point


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

    def get_points_for_all_cars(self) -> dict[int, list[Point]]:
        """Returns a list of points on the map for all cars.

        Returns:
            dict[int, list[Point]]: A mapping from car id to a list of the points on
                the map.
        """
        return self._map_state.get_points()

    @deprecated("Use get_points_for_all_cars instead")
    def get_points_positions_for_all_cars(self) -> dict[int, list[Point]]:
        """Returns a list of the points on the map for all cars. Alias for
        get_points_for_all_cars()

        Returns:
            dict[int, list[Point]]: A mapping from car id to a list of the points on
                the map.
        """
        return self.get_points_for_all_cars()

    def get_points_for_specific_car(self, car_id: int) -> list[Point] | None:
        """Returns a list of the points on the map for the specific car.

        Args:
            car_id (int): Car id
        Returns:
            list[Point] | None: A list of the points on the map or None if the car
                doesn't collect points.
        """
        points = self._map_state.get_points().get(car_id)
        return points

    @deprecated("Use get_points_for_specific_car instead")
    def get_points_positions_for_specific_car(self, car_id: int) -> list[Point] | None:
        """Returns a list of the points on the map for the specific car. Alias for
        get_points_for_specific_car()

        Args:
            car_id (int): Car id
        Returns:
            list[Point] | None: A list of the points on the map or None if the car
                doesn't collect points.
        """
        return self.get_points_for_specific_car(car_id)

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

    def get_points_amount_for_all_cars(self) -> dict[int, int]:
        """Checks how many each agent has points to collect

        Returns:
            dict[int, int]: A dict that maps car_id to a number of points to collect
        """
        points_dict = self.get_points_for_all_cars()
        return {car_id: len(point_list) if point_list else 0
                for car_id, point_list in points_dict}

    def get_points_amount_for_specific_cars(self, car_id: int) -> int | None:
        """Checks how many points the agent has to collect

        Args:
            car_id: int: The id identifying the car.

        Returns:
            int | None:  number telling how many points left for the car or None if id is invalid
        """
        return self.get_points_amount_for_all_cars().get(car_id)

    def get_which_cars_finished(self) -> dict[int, bool]:
        """Checks which agents finished

        Returns:
            dict[int, bool]: A dict that maps car_id to a bool if a car has finished
        """
        points_dict = self.get_points_for_all_cars()
        return {car_id: len(point_list) == 0
                for car_id, point_list in points_dict}

    def get_if_car_finished(self, car_id: int) -> bool | None:
        """Checks if the agent finished

        Args:
            car_id: int: The id identifying the car.

        Returns:
            bool | None: A bool telling if the car has finished or None if id is invalid
        """
        return self.get_which_cars_finished().get(car_id)
