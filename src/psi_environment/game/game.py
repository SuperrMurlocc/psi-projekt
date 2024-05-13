import random
from typing import Any
import numpy as np
from collections import deque
import pygame

class Game:
    def __init__(self, crossroads, random_seed: int = None):
        if random_seed is None:
            random_seed = random.randint(0, 2137)
        self._random_seed = random_seed
        self._timestep = 0
        self._map = crossroads
        pygame.init()
        self._screen = pygame.display.set_mode((1280, 720))
        self._clock = pygame.time.Clock()
        self._running = True

        # Preparing 2-directional queue for each connection between crossroads
        self._edges = {}
        for y in range(self._map.shape[0]):
            for x in range(y, self._map.shape[1]):
                if self._map[y, x] != 0:
                    self._edges[(y, x)] = deque()
                    self._edges[(x, y)] = deque()

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
        self.render()
        self.is_running()
        
    def get_timestep(self) -> int:
        """
        Returns timestep of the environment
        :return: timestep of the environment
        """
        return self._timestep
    
    def reset(self):
        """
        Resets environment to the initial state
        """
        raise NotImplementedError

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

        # fill the screen with a color to wipe away anything from last frame
        self._screen.fill("purple")

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        self._clock.tick(60)  # limits FPS to 60

    def is_running(self):
        return self._running

pygame.quit()