import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState


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
            pass  # TODO implement moving cars per action

    def get_map_state(self) -> MapState:
        return self._map_state
