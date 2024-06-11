from typing import Type

import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState, Road
from psi_environment.data.action import Action
from psi_environment.data.point import Point

AGENT_ID = 1


class Map:
    def __init__(
        self,
        random_seed: int,
        n_bots: int = 3,
        agent_type: Type[Car] | None = None,
        n_points: int = 3,
    ):
        self.n_points = n_points
        self._map_state = MapState(random_seed)

        self._cars: list[Car] = []
        self._agent_car_id = None

        self._random_seed = random_seed

        cars_data = self._map_state.add_cars(n_bots + 1)

        for car_id, (road_key, road_pos_idx) in cars_data.items():
            if car_id == AGENT_ID and agent_type is not None:
                car = agent_type(road_key, road_pos_idx, car_id)
                self._agent_car_id = car_id
                self._cars.append(car)
                continue

            car = DummyAgent(road_key, road_pos_idx, self._random_seed, car_id)
            self._cars.append(car)

        self._map_state.add_points(n_points)

    def step(self):
        actions = [(car, car.get_action(self._map_state)) for car in self._cars]
        actions.sort(key=lambda x: x[1])

        for car, action in actions:
            collect_points = False
            if car.get_car_id() == self._agent_car_id:
                collect_points = True

            car_moved, new_road_key, new_road_pos = self._map_state.move_car(
                car.get_car_id(), action, collect_points
            )
            if car_moved:
                car.road_key = new_road_key
                car.road_pos = new_road_pos

    def is_game_over(self) -> bool:
        return len(self._map_state.get_points()) == 0

    def get_map_state(self) -> MapState:
        return self._map_state
