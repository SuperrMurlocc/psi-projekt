import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState, Road
from psi_environment.data.car import Action


class Map:
    def __init__(self, random_seed: int, n_bots: int = 3):
        self._map_state = MapState(random_seed)

        self._cars: list[Car] = []

        self._random_seed = random_seed

        # TODO: breaks if number of cars is greater than number of roads
        roads = self._map_state.get_roads()
        road_idxs = np.random.choice(len(roads), size=n_bots)
        road_keys = [list(roads)[idx] for idx in road_idxs]

        for i, road_key in enumerate(road_keys):
            car_idx = i + 1
            road_pos_idx = self._map_state.add_car(road_key, car_idx)
            car = DummyAgent(road_key, road_pos_idx, self._random_seed, car_idx)
            self._cars.append(car)

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

    def get_map_state(self) -> MapState:
        return self._map_state
