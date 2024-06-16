from abc import abstractmethod

import numpy as np

from psi_environment.data.map_state import MapState
from psi_environment.api.environment_api import EnvironmentAPI
from psi_environment.data.action import Action


class Car:
    """The Car class serves as an abstract base class for vehicles in the simulation. It defines the basic properties and methods that all cars should have.
    """
    def __init__(self, road_key: tuple[int, int], road_pos: int, car_id: int):
        """Initializes the Car instance.

        Args:
            road_key (tuple[int, int]): A tuple representing the road on which the car is currently located.
            road_pos (int): An integer representing the car's position on the road.
            car_id (int): An integer representing the unique identifier of the car.
        """
        self.road_key = road_key
        self.road_pos = road_pos
        self._car_id = car_id

    @abstractmethod
    def get_action(self, map_state: MapState) -> Action:
        """Abstract method to determine the car's next action.

        Args:
            map_state (MapState): The current state of the map.

        Returns:
            Action: The action to be taken by the car.
        """
        pass

    def get_car_id(self):
        """Returns the car's unique identifier.

        Returns:
            _type_: The unique identifier of the car.
        """
        return self._car_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.road_key}, {self.road_pos}, {self._car_id})"


class DummyAgent(Car):
    """The DummyAgent class is a subclass of Car that implements a simple agent which makes random decisions based on a given random seed.
    """
    def __init__(
        self, road_key: tuple[int, int], road_pos: int, random_seed: int, car_id: int
    ):
        """Initializes the DummyAgent instance.

        Args:
            road_key (tuple[int, int]): The road on which the car is currently located.
            road_pos (int): The car's position on the road.
            random_seed (int): The seed used for random number generation.
            car_id (int): The unique identifier of the car.
        """
        super().__init__(road_key, road_pos, car_id)

        self._random_seed = random_seed
        self._step = 0
        self._last_action = None
        self._last_road_key = None
        self._last_road_pos = None

    def get_action(self, map_state: MapState) -> Action:
        """Determines the agent's next action based on the current state of the map.

        Args:
            map_state (MapState): The current state of the map.

        Returns:
            Action: The action to be taken by the agent.
        """
        self._step += 1

        seed = (self._random_seed * self._car_id) % 10_000 + self._step
        rng = np.random.default_rng(seed)

        api = EnvironmentAPI(map_state)

        action = rng.choice([Action.FORWARD, Action.BACK], p=[0.95, 0.05])
        if api.is_position_road_end(self.road_key, self.road_pos):
            if (
                self._last_road_key == self.road_key
                and self._last_road_pos == self.road_pos
            ):
                action = self._last_action
            else:
                available_turns = api.get_available_turns(self.road_key)
                action = rng.choice(available_turns)

        self._last_action = action
        self._last_road_key = self.road_key
        self._last_road_pos = self.road_pos
        return action
