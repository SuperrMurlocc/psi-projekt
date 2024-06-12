from abc import abstractmethod

import numpy as np

from psi_environment.data.map_state import MapState
from psi_environment.api.environment_api import EnvironmentAPI
from psi_environment.data.action import Action


class Car:
    def __init__(self, road_key: tuple[int, int], road_pos: int, car_id: int):
        self.road_key = road_key
        self.road_pos = road_pos
        self._car_id = car_id

    @abstractmethod
    def get_action(self, map_state: MapState) -> Action:
        pass

    def get_car_id(self):
        return self._car_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.road_key}, {self.road_pos}, {self._car_id})"


class DummyAgent(Car):
    def __init__(
        self, road_key: tuple[int, int], road_pos: int, random_seed: int, car_id: int
    ):
        """
        :param occupied_road: road on which the bot is
        :param random_seed: seed that will be used to take actions
        """
        super().__init__(road_key, road_pos, car_id)

        self._random_seed = random_seed
        self._step = 0
        self._last_action = None
        self._last_road_key = None
        self._last_road_pos = None

    def get_action(self, map_state: MapState) -> Action:
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
