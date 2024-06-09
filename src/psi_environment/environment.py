import random
from typing import Any, Type

import numpy as np

from psi_environment.game.game import Game
from psi_environment.data.map import Map
from psi_environment.api.environment_api import EnvironmentAPI
from psi_environment.data.car import Car


class Environment:
    def __init__(
        self,
        random_seed: int = None,
        agent_type: Type[Car] = None,
        ticks_per_second: int = 10,
        n_bots: int = 10,
        n_points: int = 3
    ):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        np.random.seed(self._random_seed)
        self._map = Map(self._random_seed, n_bots, agent_type, n_points)
        self.data = EnvironmentAPI(self._map)
        self._game = Game(
            self._map, random_seed=random_seed, ticks_per_second=ticks_per_second
        )
        self._is_running = True
        self.cost = 0

    def step(self) -> bool:
        self._map.step()
        self._game.step()
        self.cost += 1
        if self._map.is_game_over():
            self._is_running = False
            print("Game over!")
            print(f"Cost: {self.cost}")
        return self._is_running

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
