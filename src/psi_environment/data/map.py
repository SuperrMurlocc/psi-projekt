from typing import Type

import numpy as np

from psi_environment.data.car import Car, DummyAgent
from psi_environment.data.map_state import MapState, Road
from psi_environment.data.action import Action
from psi_environment.data.point import Point

AGENT_ID = 1


class Map:
    """The Map class manages the initialization of the map state and the agents. It 
    also provides higher level methods for interacting with the map state and agents, 
    like handling game steps and checking if the game is over.
    """
    def __init__(
        self,
        random_seed: int,
        n_bots: int = 3,
        agent_type: Type[Car] | None = None,
        n_points: int = 3,
        traffic_lights_percentage: float = 0.4,
        traffic_lights_length: int = 10,
    ):
        """Initializes the Map instance.

        Args:
            random_seed (int): The seed used for random number generation.
            n_bots (int, optional): The number of bots to add to the map. Defaults to 3.
            agent_type (Type[Car] | None, optional): The type of the agent car. 
                Defaults to None.
            n_points (int, optional): The number of points to be collected on the map. 
                Defaults to 3.
            traffic_lights_percentage (float, optional): The percentage of nodes with 
                traffic lights. Defaults to 0.4.
            traffic_lights_length (int, optional): The interval length for switching 
                traffic lights. Defaults to 10.
        """
        self.n_points = n_points
        self._map_state = MapState(random_seed, traffic_lights_percentage)
        self._cars: dict[int, Car] = {}
        self._agent_car_id = None
        self._random_seed = random_seed
        self._traffic_lights_length = traffic_lights_length

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
        self._step = 0

    def step(self):
        """Advances the simulation by one step.
        This method retrieves actions for each car and sends it to the map state, 
        updates the cars position based on the map state response, and switches traffic
        lights at specified intervals.
        """
        actions = [
            (
                car_id,
                car.get_action(self._map_state),
                car_id == self._agent_car_id,
            )
            for car_id, car in self._cars.items()
        ]
        action_results = self._map_state.move_cars(actions)

        for car_id, car_road_key, car_road_pos in action_results:
            car = self._cars[car_id]
            car.road_key = car_road_key
            car.road_pos = car_road_pos

        self._step += 1
        if self._step % self._traffic_lights_length == 0:
            self._map_state._switch_traffic_lights()

    def is_game_over(self) -> bool:
        """Checks if the game is over.

        Returns:
            bool: True if there are no more points to collect, False otherwise.
        """
        return len(self._map_state.get_points()) == 0

    def get_map_state(self) -> MapState:
        """Returns the reference to the map state.

        Returns:
            MapState: The reference to the map state.
        """
        return self._map_state
