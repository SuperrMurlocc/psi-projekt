import random
from typing import Any

from psi_environment.game.game import Game
from psi_environment.data.map import Map, Road
from psi_environment.api.environment_api import EnvironmentAPI


class Environment:
    def __init__(self, random_seed: int = None):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        self._map = Map(self._random_seed)
        self._map_array = self._map.get_map_array()
        self.data = EnvironmentAPI(self._map)
        self._game = Game(self._map_array, random_seed=random_seed)
        self._is_running = True

    def step(self, action: int) -> tuple[Any, float, bool]:
        """
        Accepts action provided by agent when has to decide where to go. After that environment continues simulation
        and returns another observation of the environment and cost it took by taking the action.
        :param action: an integer (in range from 0 to 2) of direction where the agent wants to go.
        :return: tuple of environment observation, cost of this action and bool stating if the agent has finished
        """
        # TODO: This requires a focus if only this will be returned.
        #  Also I'm not sure about how observation will look like.
        #  How will be direction handled so it will be consistent. I suggest something like a clock
        #  but it will require some extra checks of edges.
        #  And the implementation of it has not started


        return self._game.step(action)

    def get_timestep(self) -> int:
        """
        Returns timestep of the environment
        :return: timestep of the environment
        """
        return self._game.get_timestep()

    def reset(self):
        """
        Resets environment to the initial state
        """
        return self._game.reset()

    def is_running(self):
        self._is_running = self._game.is_running()
        return self._is_running


class Car:
    def __init__(self, occupied_road: tuple[Road, int], car_id: int):
        self.road, self.road_pos = occupied_road
        self._car_id = car_id

    def get_action(self) -> int:
        return 0

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


class DummyAgent(Car):
    def __init__(self, occupied_road: tuple[Road, int], random_seed: int, car_id: int):
        """
        :param occupied_road: road on which the bot is
        :param random_seed: seed that will be used to take actions
        """
        super().__init__(occupied_road, car_id)

        self._random_seed = random_seed
        self._step = 0

    def get_action(self) -> int:
        self._step += 1
        return self._random_seed + self._car_id + self._step % 3
