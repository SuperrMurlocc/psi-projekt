import random
from typing import Any

import numpy as np

from psi_environment.game.game import Game
from psi_environment.data.map import Map
from psi_environment.data.car import Car


class Environment:
    def __init__(
        self,
        random_seed: int = None,
        agents: list[Car] = [],
        ticks_per_second: int = 10,
    ):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        np.random.seed(self._random_seed)
        self._map = Map(self._random_seed)
        self._game = Game(
            self._map, random_seed=random_seed, ticks_per_second=ticks_per_second
        )
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
        self._map.step()
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
