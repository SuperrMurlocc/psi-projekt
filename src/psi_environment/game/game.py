from typing import Any
import pygame

class Game:
    def __init__(self, crossroads, random_seed: int = None):
        self._random_seed = random_seed
        self._timestep = 0
        self._crossroads = crossroads
        pygame.init()
        pygame.display.set_caption("Traffic simulation")
        self._screen = pygame.display.set_mode((1280, 720))
        self._clock = pygame.time.Clock()
        self._running = True

    def __del__(self):
        pygame.quit()

    def step(self, action: int) -> tuple[Any, float, bool]:
        self.render()
        self.is_running()
        
    def get_timestep(self) -> int:
        return self._timestep
    
    def reset(self):
        raise NotImplementedError

    def render(self):
        #Check for all events, such as QUIT. Probably not the right place for it, but it's a start. TODO - move it to more appropriate place.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

        self._screen.fill("white")
        # RENDER ALL GAME ELEMENTS HERE

        #
        pygame.display.flip()

        self._clock.tick(60) 

    def is_running(self):
        return self._running
    
