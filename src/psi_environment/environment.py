import random
from typing import Type

import numpy as np

from psi_environment.game.game import Game
from psi_environment.data.map import Map
from psi_environment.data.car import Car
from psi_environment.data.stop_mode import StopMode


class Environment:
    def __init__(
        self,
        agent_types: list[Type[Car]] | None = None,
        agent_type: Type[Car] | None = None,
        ticks_per_second: int = 10,
        n_bots: int = 10,
        n_points: int = 3,
        traffic_lights_percentage: float = 0.4,
        traffic_lights_length: int = 10,
        random_seed: int = None,
        stop_mode: StopMode = StopMode.ALL_FINISHED,
    ):
        """Environment class to simulate the problem of a small traffic simulation. The
        goal of the simulation is to collect all points on the map in the minimum number
        of steps.

        Args:
            agent_types (list[Type[Car]] | None, optional): list of agent types to add
                to the environment, one for each element. Defaults to None.
            agent_type (Type[Car] | None, optional): agent type to add to the
                environment. USE agent_types ARGUMENT! left for backwards compatibility.
                Defaults to None.
            ticks_per_second (int, optional): number of ticks per second.
                Defaults to 10.
            n_bots (int, optional): number of bot cars added to the environment.
                Defaults to 10.
            n_points (int, optional): number of points added to the environment for each
                car. Defaults to 3.
            traffic_lights_percentage (float, optional): percentage of valid nodes with
                traffic lights. Only nodes with 3 or more roads connected can have
                traffic lights (are valid). Defaults to 0.4.
            traffic_lights_length (int, optional): number of ticks between traffic
                lights switch. Defaults to 10.
            random_seed (int, optional): random seed for the environment.
                Defaults to None.

        Raises:
            ValueError: If both agent_type and agent_types are set.
        """
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        np.random.seed(self._random_seed)

        if agent_type is not None and agent_types is not None:
            raise ValueError("Only one of agent_type and agent_types can be set.")
        if agent_type is not None:
            agent_types = [agent_type]
        if agent_types is None:
            agent_types = []

        self._map = Map(
            random_seed=self._random_seed,
            n_bots=n_bots,
            agent_types=agent_types,
            n_points=n_points,
            traffic_lights_percentage=traffic_lights_percentage,
            traffic_lights_length=traffic_lights_length,
            stop_mode=stop_mode
        )
        self._game = Game(
            self._map, random_seed=random_seed, ticks_per_second=ticks_per_second
        )
        self._is_running = True

    def step(self) -> tuple[int, bool]:
        """Advances the simulation by one step. If the game is over (all points are
        collected), the game is stopped.

        Returns:
            tuple[int, bool]: Current cost and if the game is still running
        """
        self._map.step()
        self._game.step()
        if self._map.is_game_over():
            self._game.stop()
            print("Game over!")
            print(f"Cost: {self.get_timestep()}")
        return self.get_timestep(), self.is_running()

    def get_timestep(self) -> int:
        """Returns the current timestep.

        Returns:
            int: Current timestep
        """
        return self._game.get_timestep()

    def reset(self):
        """Resets the environment. Not implemented yet.

        Raises:
            NotImplementedError: Not implemented

        """
        raise NotImplementedError

    def is_running(self) -> bool:
        """Checks if the game is still running.

        Returns:
            bool: True if the game is running, False otherwise
        """
        self._is_running = self._game.is_running()
        return self._is_running
