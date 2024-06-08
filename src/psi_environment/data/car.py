from enum import IntEnum
from abc import abstractmethod

from psi_environment.data.map_state import MapState


class Action(IntEnum):
    RIGHT = 1
    FORWARD = 2
    LEFT = 3
    BACK = 4


class Car:
    def __init__(self, road_key: tuple[int, int], road_pos: int, car_id: int):
        self.road_key = road_key
        self.road_pos = road_pos
        self._car_id = car_id

    @abstractmethod
    def get_action(self, map_state: MapState) -> Action:
        pass

    def turn_left(self):
        pass

    def turn_right(self):
        pass

    def turn_back(self):
        pass

    def go_forward(self):
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

    def get_action(self, map_state: MapState) -> Action:
        self._step += 1
        return (self._random_seed + self._car_id + self._step) % 4 + 1
