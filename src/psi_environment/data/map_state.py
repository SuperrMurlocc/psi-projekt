import importlib.resources
from enum import IntEnum
from typing_extensions import deprecated
from copy import deepcopy

import numpy as np

from psi_environment.data.action import Action
from psi_environment.data.point import Point

NODE_CHARACTER = "x"
EMPTY_CHARACTER = "#"
H_ROAD_CHARACTER = "="
V_ROAD_CHARACTER = "|"
ROAD_CHARACTERS = {H_ROAD_CHARACTER, V_ROAD_CHARACTER}


class Road:
    """The Road class represents a road in the simulation, managing its properties,
    traffic and connections to other roads."""

    def __init__(
        self,
        length_on_map: int,
        front_node: int,
        front_indicies: tuple[int, int],
        back_node: int,
        back_indicies: tuple[int, int],
        adjacent_nodes: set,
        cars_per_length: int = 2,
        left_node: int | None = None,
        right_node: int | None = None,
        forward_node: int | None = None,
    ):
        """Initializes the Road instance.

        Args:
            length_on_map (int): The length of the road on the map.
            front_node (int): The node at the front of the road.
            front_indicies (tuple[int, int]): The indices of the front node.
            back_node (int): The node at the back of the road.
            back_indicies (tuple[int, int]): The indices of the back node.
            adjacent_nodes (set): Set of adjacent nodes.
            cars_per_length (int, optional): Number of cars per unit length of the road.
                Defaults to 2.
            left_node (int | None, optional): The node you will reach by going left at
                the intersection. Defaults to None.
            right_node (int | None, optional): The node you will reach by going right at
                the intersection. Defaults to None.
            forward_node (int | None, optional): The node you will reach by going
                straight at the intersection. Defaults to None.
        """
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

    def get_road(self) -> np.ndarray:
        """Returns the numpy array representing the car positions on the road.

        Returns:
            np.ndarray: The array of car positions on the road.
        """
        return self._road

    def get_length(self) -> int:
        """Returns the length of the road.

        Returns:
            int: The length of the road.
        """
        return self.length

    def get_inverted_position(self, pos: int) -> int:
        """Returns the inverted position on the road. Useful to get a position on the
        backwards road when a car wants to turn back.

        Args:
            pos (int): The position on the road.

        Returns:
            int: The inverted position on the road.
        """
        return self.length - 1 - pos

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.get_key()}, {repr(self._road)})"

    def __getitem__(self, idx: int):
        return self._road[idx]

    def __setitem__(self, idx, value):
        self._road[idx] = value

    def __delitem__(self, idx: int):
        self._road[idx] = 0

    def get_key(self) -> tuple[int, int]:
        """Returns the key of the road.

        Returns:
            tuple[int, int]: The key of the road.
        """
        return (self._back_node, self._front_node)

    def get_left_road_key(self) -> tuple[int, int] | None:
        """Returns the key of the left road (if any).

        Returns:
            tuple[int, int] | None: The key of the left road, or None if there is no
                left road.
        """
        if self._left_node is not None:
            return self._front_node, self._left_node
        return None

    def get_right_road_key(self) -> tuple[int, int] | None:
        """Returns the key of the right road (if any).

        Returns:
            tuple[int, int] | None: The key of the right road, or None if there is no
                right road.
        """
        if self._right_node is not None:
            return self._front_node, self._right_node
        return None

    def get_reverse_right_road_key(self) -> tuple[int, int] | None:
        """Returns the key of the reverse right road (if any).
        Reverse right road is the right road that is in the direction of the front node.

        Returns:
            tuple[int, int] | None: The key of the reverse right road, or None if there
                is no reverse right road.
        """
        if self._right_node is not None:
            return self._right_node, self._front_node
        return None

    def get_forward_road_key(self) -> tuple[int, int] | None:
        """Returns the key of the forward road (if any).

        Returns:
            tuple[int, int] | None: The key of the forward road, or None if there is no
                forward road.
        """
        if self._forward_node is not None:
            return self._front_node, self._forward_node
        return None

    def get_reverse_forward_road_key(self) -> tuple[int, int] | None:
        """Returns the key of the reverse forward road (if any).
        Reverse forward road is the front road that is in the direction of the front
        node.

        Returns:
            tuple[int, int] | None: The key of the reverse forward road, or None if
                there is no reverse forward road.
        """
        if self._forward_node is not None:
            return self._forward_node, self._front_node
        return None

    def get_backward_road_key(self) -> tuple[int, int]:
        """Returns the key of the backward road.

        Returns:
            tuple[int, int]: The key of the backward road.
        """
        return self._front_node, self._back_node

    def get_number_of_cars(self) -> int:
        """Returns the number of cars on the road.

        Returns:
            int: The number of cars on the road.
        """
        return np.count_nonzero(self._road)

    def get_traffic(self) -> int:
        """Returns the number of cars on the road. Alias for get_number_of_cars()

        Returns:
            int: The number of cars on the road.
        """
        return self.get_number_of_cars()

    def get_map_position(self, pos: int) -> tuple[int, int]:
        """Returns the map position for a given road position.

        Args:
            pos (int): The position on the road.

        Raises:
            ValueError: If the position is out of range.

        Returns:
            tuple[int, int]: The map position corresponding to the road position.
        """
        if pos < 0 or pos >= self.length:
            raise ValueError("Position out of range")
        relative_pos = 1 + pos // self._cars_per_length
        front_indices = np.array(self._front_indicies)
        back_indices = np.array(self._back_indicies)
        diff = back_indices - front_indices
        diff = np.where(diff != 0, relative_pos * np.sign(diff), 0)
        return tuple(back_indices - diff)

    def get_road_positions_by_map_position(self, map_pos: tuple[int, int]) -> int:
        """Returns the road position for a given map position.

        Args:
            map_pos (tuple[int, int]): The map position.

        Raises:
            ValueError: If the position is out of range.

        Returns:
            int: The road position corresponding to the map position.
        """
        # check if position is in range
        diff = np.array(self._back_indicies) - np.array(self._front_indicies)
        pos_diff = np.array(self._back_indicies) - np.array(map_pos)
        if np.any(diff < 0):
            diff = -diff
            pos_diff = -pos_diff

        if not (
            np.any(pos_diff == 0) and np.any(pos_diff > 0) and np.any(pos_diff < diff)
        ):
            raise ValueError("Position out of range")
        road_pos = int(np.max(pos_diff) - 1) * self._cars_per_length
        return [(self.get_key(), road_pos + i) for i in range(self._cars_per_length)]

    def is_position_road_end(self, pos_idx: int) -> bool:
        """Checks if a given position index is at the end of the road.

        Args:
            pos_idx (int): The position index to check.

        Returns:
            bool: True if the position is at the end of the road, False otherwise.
        """
        return pos_idx == self.length - 1

    def is_front_empty(self) -> bool:
        """Checks if the front position of the road is empty.

        Returns:
            bool: True if the front position is empty, False otherwise.
        """
        return self._road[0] == 0

    def get_car_on_last_position(self) -> int:
        """Returns the ID of the car at the last position of the road.

        Returns:
            int: The car at the last position.
        """
        return self._road[-1]

    def get_available_turns(self) -> list[Action]:
        """Returns a list of available turns from the current road.

        Returns:
            list[Action]: A list of available actions.
        """
        available_turns = [Action.BACK]
        if self._forward_node is not None:
            available_turns.append(Action.FORWARD)
        if self._left_node is not None:
            available_turns.append(Action.LEFT)
        if self._right_node is not None:
            available_turns.append(Action.RIGHT)
        return available_turns

    def get_available_actions(self) -> list[Action]:
        """Returns a list of available actions from the current road. Alias for
        get_available_turns()

        Returns:
            list[Action]: A list of available actions.
        """
        return self.get_available_turns()


class Direction(IntEnum):
    """The Direction enum represents the possible directions on the map topology."""

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def relative_direction(self, other: "Direction") -> "Direction":
        """Returns the relative direction compared to another direction.

        Args:
            other (Direction): The other direction to compare.

        Returns:
            Direction: The relative direction.
        """
        return Direction((other - self + 4) % 4)


class TrafficLight:
    """The TrafficLight class represents a traffic light at a specific node, managing
    the blocked directions and switching states"""

    def __init__(
        self,
        node: int,
        up_node: int | None = None,
        down_node: int | None = None,
        left_node: int | None = None,
        right_node: int | None = None,
        blocked_direction: Direction = Direction.UP,
    ):
        """Initializes the TrafficLight instance.

        Args:
            node (int): The node where the traffic light is located.
            up_node (int | None, optional): The node in the upward direction.
                Defaults to None.
            down_node (int | None, optional): The node in the downward direction.
                Defaults to None.
            left_node (int | None, optional): The node in the left direction.
                Defaults to None.
            right_node (int | None, optional): The node in the right direction.
                Defaults to None.
            blocked_direction (Direction, optional): The direction currently blocked by
                the traffic light. Defaults to Direction.UP.
        """
        self._node = node
        self._up_node = up_node
        self._down_node = down_node
        self._left_node = left_node
        self._right_node = right_node
        self._blocked_direction = blocked_direction

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._node}, {self._blocked_direction})"

    def get_blocked_road_keys(self) -> list[tuple[int, int]]:
        """Returns a list of road keys blocked by the traffic light. Traffic light
        blocks all roads in the same AND opposite direction as the blocked direction,
        which means that e.g. direction UP blocks both roads UP and DOWN, and LEFT
        blocks both roads LEFT and RIGHT.


        Returns:
            list[tuple[int, int]]:  A list of blocked road keys.
        """
        road_keys = []
        if self._blocked_direction in (Direction.UP, Direction.DOWN):
            if self._up_node is not None:
                road_keys.append((self._up_node, self._node))
            if self._down_node is not None:
                road_keys.append((self._down_node, self._node))
        elif self._blocked_direction in (Direction.LEFT, Direction.RIGHT):
            if self._left_node is not None:
                road_keys.append((self._left_node, self._node))
            if self._right_node is not None:
                road_keys.append((self._right_node, self._node))
        return road_keys

    def switch_lights(self):
        """Switches the traffic light to block the next direction."""
        self._blocked_direction = Direction((self._blocked_direction + 1) % 4)


def get_map(filename="sample_map.txt") -> np.ndarray:
    """Generates an array representation of a sample map from a text file.

    Args:
        filename (str, optional): The name of the file containing the map. Defaults to
            "sample_map.txt".

    Returns:
        np.ndarray: A numpy array representing the map.
    """
    with importlib.resources.open_text("psi_environment.game.resources", filename) as f:
        content = f.read()

    map_array = content.split()
    map_array = np.array([[*row] for row in map_array])
    return map_array


def get_node_indices(map_array) -> dict[int, tuple[int, int]]:
    """Finds node indices of a sample map.

    Args:
        map_array (np.ndarray): A numpy array representing the map.

    Returns:
        dict[int, tuple[int, int]]: A dictionary where keys are node IDs and values are
            tuples representing the (x, y) coordinates of the nodes.
    """
    node_indices = {}
    id = 0
    for y in range(map_array.shape[0]):
        for x in range(map_array.shape[1]):
            if map_array[y][x] == NODE_CHARACTER:
                node_indices[id] = (x, y)
                id += 1
    return node_indices


def create_adjacency_matrix(
    content: np.ndarray, node_indices: dict[int, tuple[int, int]]
) -> np.ndarray:
    """Generates the adjacency matrix of a sample map from the map array.

    Args:
        content (np.ndarray): A numpy array representing the map.
        node_indices (dict[int, tuple[int, int]]): A dictionary where keys are node IDs
            and values are tuples representing the (x, y) coordinates of the nodes.

    Returns:
        np.ndarray: The adjacency matrix of the map.
    """
    n_nodes = len(node_indices)
    indices_node = {v: k for k, v in node_indices.items()}

    adjacency_matrix = np.full((n_nodes, n_nodes), np.nan)

    directions = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    for node_id, (x, y) in node_indices.items():
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
                neighbor_id = indices_node[(nx, ny)]
                # subtract 1 because we don't count the node itself
                adjacency_matrix[node_id, neighbor_id] = route_length - 1

    return adjacency_matrix


def get_indices_road_keys(
    node_indices: dict[int, tuple[int, int]], adjacency_matrix: np.ndarray
) -> dict[tuple[int, int], tuple[int, int]]:
    """Finds the road keys for the map positions indices. It contains only road keys
    that are in ascending node order. That means for given map position, there will also
    be a road with reversed node order, e.g.:
    map_position = (0, 1)
    road_key = indices_road_keys[map_position]
    reversed_road_key = (road_key[1], road_key[0]) # this road also is on given map pos

    Args:
        node_indices (dict[int, tuple[int, int]]): mapping from node id to map position
        adjacency_matrix (np.ndarray): adjacency matrix

    Returns:
        dict[tuple[int, int], tuple[int, int]]: mapping from map position to road key
    """
    indicies_road_keys = {}
    for x_id, (x_x, x_y) in node_indices.items():
        for y_id, (y_x, y_y) in node_indices.items():
            if x_id > y_id:
                continue
            if not np.isnan(adjacency_matrix[x_id, y_id]):
                # this is always true with the rest of our logic, but if it ever happens
                # to be changed, this will blow up and prevent bugs
                assert x_x <= y_x
                assert x_y <= y_y

                keys = [
                    (x, y) for x in range(x_x, y_x + 1) for y in range(x_y, y_y + 1)
                ]
                keys.remove((x_x, x_y))
                keys.remove((y_x, y_y))
                for key in keys:
                    indicies_road_keys[key] = (x_id, y_id)
    return indicies_road_keys


def create_edges(
    node_indices: dict[int, tuple[int, int]], adjacency_matrix: np.ndarray
) -> dict[tuple[int, int], Direction]:
    """Creates edges between nodes based on the adjacency matrix.

    Args:
        node_indices (dict[int, tuple[int, int]]): A dictionary where keys are node IDs
            and values are tuples representing the (x, y) coordinates of the nodes.
        adjacency_matrix (np.ndarray): The adjacency matrix of the map.

    Returns:
        dict[tuple[int, int], Direction]: A dictionary where keys are tuples
            representing edges between nodes and values are Direction enums indicating
            the direction of the edge.
    """
    edges = {}
    for x_id, (x_x, x_y) in node_indices.items():
        for y_id, (y_x, y_y) in node_indices.items():
            if not np.isnan(adjacency_matrix[x_id, y_id]):
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

                edges[(x_id, y_id)] = direction
    return edges


def create_roads(
    edges: dict[tuple[int, int], Direction],
    adjacency_matrix: np.ndarray,
    node_indices: dict[int, tuple[int, int]],
) -> dict[tuple[int, int], Road]:
    """Creates roads based on edges and the adjacency matrix.

    Args:
        edges (dict[tuple[int, int], Direction]): A dictionary where keys are tuples
            representing edges between nodes and values are Direction enums indicating
            the direction of the edge.
        adjacency_matrix (np.ndarray): The adjacency matrix of the map.
        node_indices (dict[int, tuple[int, int]]):  A dictionary where keys are node IDs
            and values are tuples representing the (x, y) coordinates of the nodes.

    Returns:
        dict[tuple[int, int], Road]: A dictionary where keys are tuples representing
            edges between nodes and values are Road objects.
    """
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


def create_traffic_lights(
    edges: dict[tuple[int, int], Direction],
    adjacency_matrix: np.ndarray,
    percentage_of_nodes: float = 0.4,
) -> dict[int, TrafficLight]:
    """Creates traffic lights for nodes based on the adjacency matrix and a specified
    percentage of nodes.

    Args:
        edges (dict[tuple[int, int], Direction]): A dictionary where keys are tuples
            representing edges between nodes and values are Direction enums indicating
            the direction of the edge.
        adjacency_matrix (np.ndarray): The adjacency matrix of the map.
        percentage_of_nodes (float, optional): The percentage of nodes to have traffic
            lights. Defaults to 0.4.

    Returns:
        dict[int, TrafficLight]: A dictionary where keys are node IDs and values are
            TrafficLight objects.
    """
    node_connections = {}
    for node_id in range(adjacency_matrix.shape[0]):
        n_of_connections = np.count_nonzero(~np.isnan(adjacency_matrix[node_id]))
        node_connections[node_id] = n_of_connections

    available_nodes = [
        node_id for node_id in node_connections.keys() if node_connections[node_id] > 2
    ]

    traffic_light_nodes = np.random.choice(
        available_nodes,
        np.round(len(available_nodes) * percentage_of_nodes).astype(int),
        replace=False,
    )

    traffic_lights = {}
    for node in traffic_light_nodes:
        adjacent_nodes = [edge[1] for edge in edges.keys() if edge[0] == node]

        up_node = None
        down_node = None
        left_node = None
        right_node = None

        for adjacent_node in adjacent_nodes:
            node_direction = edges[(adjacent_node, node)]

            if node_direction == Direction.LEFT:
                right_node = adjacent_node
            elif node_direction == Direction.RIGHT:
                left_node = adjacent_node
            elif node_direction == Direction.UP:
                down_node = adjacent_node
            elif node_direction == Direction.DOWN:
                up_node = adjacent_node

        traffic_light = TrafficLight(
            node=node,
            up_node=up_node,
            down_node=down_node,
            left_node=left_node,
            right_node=right_node,
        )
        traffic_lights[node] = traffic_light

    return traffic_lights


class MapState:
    """The MapState class manages the state of the map, including roads, cars, and
    traffic lights. It defines the actions that can be taken in the environment and the
    rules of the environment.
    """

    def __init__(self, random_seed: int, traffic_light_percentage: float = 0.4):
        """Initializes the MapState instance.

        Args:
            random_seed (int): The seed used for random number generation.
            traffic_light_percentage (float, optional): The percentage of nodes with
                traffic lights. Defaults to 0.4.
        """
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
        self._indices_road_keys = get_indices_road_keys(
            self._node_indices, self._adjacency_matrix
        )
        self._traffic_lights = create_traffic_lights(
            self._edges, self._adjacency_matrix, traffic_light_percentage
        )
        self._cars: dict[int, tuple[tuple[int, int], int]] = {}
        self._points: dict[int, list[Point]] = {}

    def _add_car(
        self, car_id: int, road_key: tuple[int, int], road_pos: int | None = None
    ):
        """Adds a car to the map at a specified road.

        Args:
            road_key (tuple[int, int]): The key of the road where the car is added.
            car_id (int): The unique identifier of the car.
        """
        road = self._roads[road_key]
        if road_pos is None:
            road_pos = np.random.randint(road.length)
        road.get_road()[road_pos] = car_id
        self._cars[car_id] = (road_key, road_pos)

    def add_cars(self, n: int) -> dict[int, tuple[tuple[int, int], int]]:
        """Adds a specified number of cars to the map.

        Args:
            n (int): The number of cars to add.

        Raises:
            ValueError: If the number of cars is greater than the number of roads.

        Returns:
            dict[int, tuple[tuple[int, int], int]]: A dictionary of car IDs and
                their positions.
        """
        # TODO: breaks if number of cars is greater than number of roads
        if n > len(self._roads):
            raise ValueError("Number of cars is greater than number of roads")

        road_idxs = np.random.choice(len(self._roads), size=n, replace=False)
        road_keys = [list(self._roads)[idx] for idx in road_idxs]

        for i, road_key in enumerate(road_keys):
            car_idx = i + 1
            self._add_car(car_id=car_idx, road_key=road_key)

        return self._cars

    def add_points(self, n: int, agents_idxs: list[int]) -> dict[int, list[Point]]:
        """Adds a specified number of points to the map, n for each agent.

        Args:
            n (int): The number of points to add.
            agents_idxs (list[int]): Indexes of agents

        Returns:
            dict[int, list[Point]]: A dictionary of agent IDs and their points.
        """
        road_tile_positions = self.get_road_tiles_map_positions()
        node_tile_positions = self.get_node_tiles_map_positions()

        tile_positions = road_tile_positions + node_tile_positions
        tile_idxs = np.random.choice(len(tile_positions), size=n, replace=False)

        points: list[Point] = []

        indicies_node = {
            position: node for node, position in self._node_indices.items()
        }

        for tile_idx in tile_idxs:
            point_position = tile_positions[tile_idx]
            if point_position in node_tile_positions:
                node = indicies_node[point_position]
                point = Point(map_position=point_position, node=node)
            else:
                road_positions = self.get_road_position_by_map_position(point_position)
                point = Point(
                    map_position=point_position, road_positions=road_positions
                )
            points.append(point)

        for agent_idx in agents_idxs:
            self._points[agent_idx] = deepcopy(points)

        return self._points

    def move_cars(
        self, actions: list[tuple[int, Action]]
    ) -> list[tuple[int, tuple[int, int], int]]:
        """Moves cars based on the given actions.

        Args:
            actions (list[tuple[int, Action]]): A list of actions to perform.

        Returns:
            list[tuple[int, tuple[int, int], int]]: A list of results of the actions. It
                contains only the cars that moved and their new positions. Cars that
                have not moved are not included in the list.
        """
        road_actions = {}
        node_actions = {}
        results = []

        actions.sort(key=lambda x: x[1])  # sort by action
        for car_id, action in actions:
            car_road_key = self._cars[car_id][0]
            car_road_pos = self._cars[car_id][1]
            current_road = self.get_road(car_road_key)

            if current_road.is_position_road_end(car_road_pos):
                node_actions[car_id] = action
            else:
                road_actions[car_id] = action

        move_requests = []

        for car_id, action in road_actions.items():
            car_road_key = self._cars[car_id][0]
            car_road_pos = self._cars[car_id][1]
            current_road = self.get_road(car_road_key)

            if action == Action.FORWARD:
                next_pos = car_road_pos + 1
                move_requests.append((car_id, current_road, next_pos))

            elif action == Action.BACK:
                inv_road_key = current_road.get_backward_road_key()
                next_road = self.get_road(inv_road_key)
                inv_pos = current_road.get_inverted_position(car_road_pos)
                move_requests.append((car_id, next_road, inv_pos))

        for car_id, action in node_actions.items():
            car_road_key = self._cars[car_id][0]
            car_road_pos = self._cars[car_id][1]
            current_road = self.get_road(car_road_key)
            blocked_road_keys = []
            traffic_light = self.get_traffic_light(car_road_key[1])
            if traffic_light is not None:
                blocked_road_keys = traffic_light.get_blocked_road_keys()

            if current_road.get_key() in blocked_road_keys:
                continue

            next_road_key = None
            if action == Action.RIGHT:
                next_road_key = current_road.get_right_road_key()
            elif action == Action.FORWARD:
                next_road_key = current_road.get_forward_road_key()
            elif action == Action.LEFT:
                next_road_key = current_road.get_left_road_key()
            elif action == Action.BACK:
                next_road_key = current_road.get_backward_road_key()

            if action in (Action.FORWARD, Action.LEFT, Action.BACK):
                # check if need to give way to right car
                right_road_key = current_road.get_reverse_right_road_key()
                right_road = self.get_road(right_road_key) if right_road_key else None
                if right_road is not None and right_road_key not in blocked_road_keys:
                    right_car = right_road.get_car_on_last_position()
                    if right_car in node_actions:
                        continue

            if action in (Action.LEFT, Action.BACK):
                # check if need to give way to front car
                front_road_key = current_road.get_reverse_forward_road_key()
                front_road = self.get_road(front_road_key) if front_road_key else None
                if front_road is not None and front_road_key not in blocked_road_keys:
                    front_car = front_road.get_car_on_last_position()
                    if front_car in node_actions:
                        front_car_action = node_actions[front_car]
                        # always give way to car driving forward
                        if front_car_action == Action.FORWARD:
                            continue
                        # if turning left, give way to car driving right
                        elif front_car_action == Action.RIGHT and action == Action.LEFT:
                            continue

            # TODO fix deadlock if 4 cars arive to the same node
            # TODO check for cars that could move after car blocking them moved away

            next_road = self.get_road(next_road_key) if next_road_key else None
            if next_road is None:
                continue

            move_requests.append((car_id, next_road, 0))

        for car_id, road, road_pos in move_requests:
            car_id, car_moved, car_road_key, car_road_pos = self._move_car(
                car_id, road, road_pos
            )
            if car_moved:
                results.append((car_id, car_road_key, car_road_pos))

        return results

    def _move_car(self, car_id: int, next_road: Road, next_road_pos: int):
        """Moves a specific car to a new position.

        Args:
            car_id (int): The ID of the car.
            road (Road): The road where the car is moved.
            road_pos (int): The new position on the road.

        Returns:
            tuple[int, bool, tuple[int, int], int]: The result of the move operation.
        """
        prev_road_key = self._cars[car_id][0]
        prev_road_pos = self._cars[car_id][1]

        if next_road[next_road_pos] != 0:
            return car_id, False, prev_road_key, prev_road_pos

        next_road[next_road_pos] = car_id
        next_road_key = next_road.get_key()
        self._cars[car_id] = (next_road_key, next_road_pos)
        prev_road = self.get_road(prev_road_key)
        prev_road[prev_road_pos] = 0
        self._update_collected_points(
            prev_road_key, next_road_key, next_road_pos, car_id
        )
        return car_id, True, next_road_key, next_road_pos

    def _update_collected_points(
        self,
        prev_road_key: tuple[int, int],
        next_road_key: tuple[int, int],
        next_road_pos: int,
        car_id: int,
    ):
        """Updates the collected points based on the car's new position.

        Args:
            prev_road_key (tuple[int, int]): The key of the road where the car was
                located.
            next_road_key (tuple[int, int]): The key of the road where the car is
                located.
            next_road_pos (int): The position of the car on the road.
            car_id (int): Id of a car
        """
        if car_id not in self._points.keys():
            return

        agent_points = self._points[car_id]
        if prev_road_key != next_road_key and next_road_pos == 0:
            # Car crossed a node
            node_crossed = self._roads[prev_road_key]._front_node
            for agent_point in agent_points:
                if agent_point.node == node_crossed:
                    agent_points.remove(agent_point)
                    break

        car_map_position = self.get_map_position_by_road_position(
            next_road_key, next_road_pos
        )

        for agent_point in agent_points:
            if agent_point.map_position == car_map_position:
                agent_points.remove(agent_point)
                break

    def _switch_traffic_lights(self):
        """Switches the state of all traffic lights on the map."""
        for traffic_light in self._traffic_lights.values():
            traffic_light.switch_lights()

    def get_road_tiles_map_positions(self) -> list[tuple[int, int]]:
        """Returns the positions of all road tiles on the map.

        Returns:
            list[tuple[int, int]]: A list of positions of road tiles.
        """
        road_tiles = []
        for y in range(self._map_array.shape[0]):
            for x in range(self._map_array.shape[1]):
                if self._map_array[y][x] in ROAD_CHARACTERS:
                    road_tiles.append((x, y))
        return road_tiles

    def get_node_tiles_map_positions(self) -> list[tuple[int, int]]:
        """Returns the positions of all node tiles on the map.

        Returns:
            list[tuple[int, int]]: A list of positions of node tiles.
        """
        return list(self._node_indices.values())

    def get_road_position_by_map_position(
        self, map_position: tuple[int, int]
    ) -> list[tuple[tuple[int, int], int]]:
        """Get the road positions by the map position.

        Args:
            map_position (tuple[int, int]): map position

        Returns:
            list[tuple[tuple[int, int], int]]: road positions that correspond to the map
                position
        """
        road_positions = []
        if map_position not in self._indices_road_keys:
            return road_positions

        road_key = self._indices_road_keys[map_position]
        road = self._roads[road_key]
        backward_road = self._roads[road.get_backward_road_key()]

        road_positions += road.get_road_positions_by_map_position(map_position)
        road_positions += backward_road.get_road_positions_by_map_position(map_position)

        return road_positions

    def get_adjacency_matrix_size(self) -> int:
        """Returns the size of the adjacency matrix.

        Returns:
            int: The size of the adjacency matrix.
        """
        return self._adjacency_matrix.shape[0]

    def get_adjacency_matrix(self) -> np.ndarray:
        """Returns the adjacency matrix.

        Returns:
            np.ndarray: The adjacency matrix.
        """
        return self._adjacency_matrix

    def get_map_array(self) -> np.ndarray:
        """Returns the map array.

        Returns:
            np.ndarray: The map array.
        """
        return self._map_array

    def get_roads(self) -> dict[tuple[int, int], Road]:
        """Returns the roads on the map.

        Returns:
            dict[tuple[int, int], Road]: A dictionary of roads.
        """
        return self._roads

    def get_road(self, key: tuple[int, int]) -> Road | None:
        """Returns a specific road based on its key.

        Args:
            key (tuple[int, int]): The key of the road.

        Returns:
            Road | None: The road corresponding to the key, or None if there is no road.
        """
        return self._roads.get(key, None)

    def get_traffic_lights(self) -> dict[int, TrafficLight]:
        """Returns the traffic lights on the map.

        Returns:
            dict[int, TrafficLight]: A dictionary of traffic lights.
        """
        return self._traffic_lights

    def get_traffic_light(self, node_id: int) -> TrafficLight | None:
        """Returns a specific traffic light based on its node ID.

        Args:
            node_id (int): The ID of the node.

        Returns:
            TrafficLight | None: The traffic light corresponding to the node ID, or
                None if there is no traffic light.
        """
        return self._traffic_lights.get(node_id, None)

    def get_cars(self) -> dict[int, tuple[tuple[int, int], int]]:
        """Returns the cars on the map.

        Returns:
            dict[int, tuple[tuple[int, int], int]]: A dictionary of cars and their positions.
        """
        return self._cars

    def get_points(self) -> dict[int, list[Point]]:
        """Returns the points on the map.

        Returns:
            dict[int, tuple[int, int]]: A dictionary of points and their positions.
        """
        return self._points

    def get_number_of_node_connections(self, node_id: int) -> int:
        """Returns the number of connections for a specific node.

        Args:
            node_id (int): The ID of the node.

        Returns:
            int: The number of connections for the node.
        """
        return np.count_nonzero(~np.isnan(self._adjacency_matrix[node_id]))

    def get_node_map_position(self, node_id: int) -> tuple[int, int]:
        """Returns the map position of a specific node.

        Args:
            node_id (int): The ID of the node.

        Returns:
            tuple[int, int]: The map position of the node.
        """
        return self._node_indices[node_id]

    def get_map_position_by_road_position(
        self, road_key: tuple[int, int], road_pos: int
    ) -> tuple[int, int]:
        """Returns the map position for a specific road position.

        Args:
            road_key (tuple[int, int]): The key of the road.
            road_pos (int): The position on the road.

        Returns:
            tuple[int, int]: The map position corresponding to the road position.
        """
        return self._roads[road_key].get_map_position(road_pos)

    @deprecated("Use get_map_position_by_road_position instead")
    def get_road_position_map_position(
        self, road_key: tuple[int, int], road_pos: int
    ) -> tuple[int, int]:
        """Returns the road position for a specific map position.
        Alias for get_map_position_by_road_position, left for backward compatibility.

        Args:
            road_key (tuple[int, int]): The key of the road.
            road_pos (int): The position on the road.

        Returns:
            tuple[int, int]: The road position corresponding to the map position.
        """
        return self.get_map_position_by_road_position(road_key, road_pos)
