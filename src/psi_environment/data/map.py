from typing import Type

import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState, Road
from psi_environment.data.car import Action
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
        self._points: list[Point] = []

        self._cars: list[Car] = []
        self._agent_car = None

        self._random_seed = random_seed

        cars_data = self._map_state.add_cars(n_bots + 1)

        for car_id, road_key, road_pos_idx in cars_data:
            if car_id == AGENT_ID and agent_type is not None:
                car = agent_type(road_key, road_pos_idx, car_id)
                self._agent_car = car
                self._cars.append(car)
                continue

            car = DummyAgent(road_key, road_pos_idx, self._random_seed, car_id)
            self._cars.append(car)

        road_tile_positions = self._map_state.get_road_tiles_map_positions()
        if self._agent_car is not None:
            car_position = self._map_state.get_road_position_map_position(
                self._agent_car.road_key, self._agent_car.road_pos
            )
            road_tile_positions.remove(car_position)
        road_tile_idxs = np.random.choice(len(road_tile_positions), size=n_points)

        for i, road_tile_idx in enumerate(road_tile_idxs):
            point_id = i + 1
            point_position = road_tile_positions[road_tile_idx]
            point = Point(point_position, point_id)
            self._points.append(point)

    def step(self):
        actions = [(car, car.get_action(self._map_state)) for car in self._cars]
        actions.sort(key=lambda x: x[1])

        for car, action in actions:
            current_road = self._map_state.get_road(car.road_key)
            if action == Action.BACK:
                inv_road_key = current_road.get_backward_road_key()
                next_road = self._map_state.get_road(inv_road_key)
                inv_pos = current_road.get_inverted_position(car.road_pos)

                if next_road[inv_pos] == 0:
                    self._move_car(car, next_road, inv_pos)
                continue

            # Car is not at the end of the road
            if current_road[-1] != car.get_car_id():
                if action == Action.FORWARD:
                    next_pos = car.road_pos + 1
                    if current_road[next_pos] == 0:
                        self._move_car(car, current_road, next_pos)
                continue

            # Car is at the end of the road
            next_road_key = None
            if action == Action.LEFT:
                next_road_key = current_road.get_left_road_key()
            elif action == Action.RIGHT:
                next_road_key = current_road.get_right_road_key()
            elif action == Action.FORWARD:
                next_road_key = current_road.get_forward_road_key()
            next_road = (
                self._map_state.get_road(next_road_key) if next_road_key else None
            )
            if next_road and next_road[0] == 0:
                next_pos = 0
                self._move_car(car, next_road, next_pos)

    def _move_car(self, car: Car, road: Road, road_pos: int):
        current_road = self._map_state.get_road(car.road_key)
        current_road[car.road_pos] = 0
        road[road_pos] = car.get_car_id()
        car.road_pos = road_pos
        car.road_key = road.get_key()
        if car == self._agent_car:
            self._update_collected_points(car)

    def _update_collected_points(self, car: Car):
        for i, point in enumerate(self._points):
            car_map_position = self._map_state.get_road_position_map_position(
                car.road_key, car.road_pos
            )
            if point.map_position == car_map_position:
                self._points.pop(i)
                break

    def is_game_over(self) -> bool:
        return len(self._points) == 0

    def get_map_state(self) -> MapState:
        return self._map_state
