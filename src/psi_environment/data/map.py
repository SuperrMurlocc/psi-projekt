from typing import Type, List

import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState, Road
from psi_environment.data.action import Action
from psi_environment.data.point import Point


class Map:
    def __init__(
        self,
        random_seed: int,
        n_bots: int = 3,
        agent_types: List[Type[Car]] | None = None,
        n_points: int = 3,
        traffic_lights_percentage: float = 0.4,
        traffic_lights_length: int = 10,
    ):
        self.n_points = n_points
        self._map_state = MapState(random_seed, traffic_lights_percentage)
        self._cars: dict[int, Car] = {}
        self._agents: dict[int, Car] = {}
        self._random_seed = random_seed
        self._traffic_lights_length = traffic_lights_length

        n_agents = len(agent_types) if agent_types else 0

        cars_data = self._map_state.add_cars(n_bots + n_agents)

        agent_iter = 0

        for car_id, (road_key, road_pos_idx) in cars_data.items():
            if agent_types and agent_iter < n_agents:
                agent_type = agent_types[agent_iter]
                car = agent_type(road_key, road_pos_idx, car_id)
                self._agents[car_id] = car
                agent_iter += 1
            else:
                car = DummyAgent(road_key, road_pos_idx, self._random_seed, car_id)
            self._cars[car_id] = car

        self._map_state.add_points(n_points)
        self._step = 0

    def step(self):
        actions = [
            (
                car_id,
                car.get_action(self._map_state),
                car_id in self._agents,
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

        self._step += 1
        if self._step % self._traffic_lights_length == 0:
            self._map_state._switch_traffic_lights()

    def is_game_over(self) -> bool:
        return len(self._map_state.get_points()) == 0

    def get_map_state(self) -> MapState:
        return self._map_state
