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

        self._cars: dict[int, Car] = {}
        self._agent_car_id = None

        self._random_seed = random_seed

        cars_data = self._map_state.add_cars(n_bots + 1)

        for car_id, (road_key, road_pos_idx) in cars_data.items():
            if car_id == AGENT_ID and agent_type is not None:
                car = agent_type(road_key, road_pos_idx, car_id)
                self._agent_car_id = car_id
                self._cars[car_id] = car
                continue

            car = DummyAgent(road_key, road_pos_idx, self._random_seed, car_id)
            self._cars[car_id] = car

        self._map_state.add_points(n_points)

    def step(self):
        actions = [
            (
                car_id,
                car.get_action(self._map_state),
                car_id == self._agent_car_id,
            )
            for car_id, car in self._cars.items()
        ]
        actions.sort(key=lambda x: x[1])
        action_results = self._map_state.move_cars(actions)

        for car_id, car_moved, car_road_key, car_road_pos in action_results:
            car = self._cars[car_id]
            if car_moved:
                car.road_key = car_road_key
                car.road_pos = car_road_pos

    def is_game_over(self) -> bool:
        return len(self._map_state.get_points()) == 0

    def get_map_state(self) -> MapState:
        return self._map_state
