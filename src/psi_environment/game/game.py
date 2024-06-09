from typing import Any
import random
import pygame
import importlib.resources


from psi_environment.data.map import Map


class Game:
    def __init__(self, map: Map, random_seed: int = None):
        self._random_seed = random_seed
        self._timestep = 0
        self._map = map
        self._crossroads = map.get_map_state().get_map_array()
        pygame.init()
        pygame.display.set_caption("Traffic simulation")
        self._screen = pygame.display.set_mode((1280, 768))
        self._clock = pygame.time.Clock()
        self._running = True
        self._init_images()
        # no crossroad tile yet

    def _init_images(self):
        with importlib.resources.path(
            "psi_environment.game.resources", "road_vertical1.png"
        ) as road_vert_path:
            self.road_vert = pygame.image.load(str(road_vert_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "road_horizontal1.png"
        ) as road_hori_path:
            self.road_hori = pygame.image.load(str(road_hori_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "crossroad1.png"
        ) as crossroad_path:
            self.crossroad = pygame.image.load(str(crossroad_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "grass.png"
        ) as grass_path:
            self.grass = pygame.image.load(str(grass_path))

    def __del__(self):
        pygame.quit()

    def step(self, action: int) -> tuple[Any, float, bool]:
        self.render()
        self.is_running()
        print("###")
        for car in self._map._cars:
            print(car._car_id, car.road_key, car.road_pos)
        print("###")

    def get_timestep(self) -> int:
        return self._timestep

    def reset(self):
        raise NotImplementedError

    def render(self):
        # Check for all events, such as QUIT. Probably not the right place for it, but it's a start. TODO - move it to more appropriate place.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

        TILE_SIZE = 32

        self._screen.fill("black")
        # RENDER MAP FROM FILE
        for idy, y in enumerate(self._crossroads):
            for idx, x in enumerate(y):
                if x == "x":
                    self.crossroad = pygame.transform.scale(
                        self.crossroad, (TILE_SIZE, TILE_SIZE)
                    )
                    self._screen.blit(
                        self.crossroad, [idx * TILE_SIZE, idy * TILE_SIZE]
                    )
                elif x == "=":
                    self.road_hori = pygame.transform.scale(
                        self.road_hori, (TILE_SIZE, TILE_SIZE)
                    )
                    self._screen.blit(
                        self.road_hori, [idx * TILE_SIZE, idy * TILE_SIZE]
                    )
                elif x == "|":
                    self.road_vert = pygame.transform.scale(
                        self.road_vert, (TILE_SIZE, TILE_SIZE)
                    )
                    self._screen.blit(
                        self.road_vert, [idx * TILE_SIZE, idy * TILE_SIZE]
                    )
                elif x == "#":
                    self.grass = pygame.transform.rotate(self.grass, 90)
                    self.grass = pygame.transform.scale(
                        self.grass, (TILE_SIZE, TILE_SIZE)
                    )
                    self._screen.blit(self.grass, [idx * TILE_SIZE, idy * TILE_SIZE])

        pygame.display.update()
        pygame.display.flip()

        self._clock.tick(60)

    def is_running(self):
        return self._running
