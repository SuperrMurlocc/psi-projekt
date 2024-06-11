import random
from typing import Any, Type

import numpy as np

from psi_environment.game.game import Game
from psi_environment.data.map import Map
from psi_environment.data.car import Car


class Environment:
    def __init__(
        self,
        agent_type: Type[Car] | None = None,
        ticks_per_second: int = 10,
        n_bots: int = 10,
        n_points: int = 3,
        random_seed: int = None,
    ):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        np.random.seed(self._random_seed)
        self._map = Map(self._random_seed, n_bots, agent_type, n_points)
        self._game = Game(
            self._map, random_seed=random_seed, ticks_per_second=ticks_per_second
        )
        self._is_running = True

    def step(self) -> tuple[int, bool]:
        self._map.step()
        self._game.step()
        if self._map.is_game_over():
            self._game.stop()
            print("Game over!")
            print(f"Cost: {self.get_timestep()}")
        return self.get_timestep(), self.is_running()

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
