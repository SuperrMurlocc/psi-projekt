from typing import Any
import random
import pygame
import importlib.resources


from psi_environment.data.map import Map
from enum import IntEnum


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


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

        with importlib.resources.path(
            "psi_environment.game.resources", "car_left.png"
        ) as car_left_path:
            self.car_left = pygame.image.load(str(car_left_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_right.png"
        ) as car_right_path:
            self.car_right = pygame.image.load(str(car_right_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_up.png"
        ) as car_up_path:
            self.car_up = pygame.image.load(str(car_up_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_down.png"
        ) as car_down_path:
            self.car_down = pygame.image.load(str(car_down_path))

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
        # Check for all events, such as QUIT. Probably not the right place for it, but it's a start. TODO - move it to more appropriate place.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

        TILE_SIZE = 32
        CAR_SIZE = 16
        self._screen.fill("black")
        # RENDER MAP FROM FILE
        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        my_font = pygame.font.SysFont("Comic Sans MS", 10)
        count = 0
        for idy, y in enumerate(self._crossroads):
            for idx, x in enumerate(y):
                if x == "x":
                    self.crossroad = pygame.transform.scale(
                        self.crossroad, (TILE_SIZE, TILE_SIZE)
                    )
                    text_surface = my_font.render(f"{count}", False, (255, 255, 255))
                    count += 1
                    self._screen.blit(text_surface, [idx * TILE_SIZE, idy * TILE_SIZE])
                    # self._screen.blit(
                    #     self.crossroad, [idx * TILE_SIZE, idy * TILE_SIZE]
                    # )
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

        print("###")
        rev_dict = {v: k for k, v in self._map._map_state._node_indices.items()}
        for car in self._map._cars:
            print(car._car_id, car.road_key, car.road_pos)
            print(rev_dict[car.road_key[0]])
            pos = rev_dict[car.road_key[0]]
            direction = self._map._map_state._edges[car.road_key]
            x, y = pos

            match direction:
                case Direction.UP:
                    self._screen.blit(
                        pygame.transform.scale(self.car_up, (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 0) * TILE_SIZE + 1 * CAR_SIZE,
                            (y - 1) * TILE_SIZE - (car.road_pos - 1) * CAR_SIZE,
                        ],
                    )
                case Direction.DOWN:
                    self._screen.blit(
                        pygame.transform.scale(self.car_down, (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 0) * TILE_SIZE + 0 * CAR_SIZE,
                            (y + 1) * TILE_SIZE + (car.road_pos) * CAR_SIZE,
                        ],
                    )
                case Direction.LEFT:
                    self._screen.blit(
                        pygame.transform.scale(self.car_left, (CAR_SIZE, CAR_SIZE)),
                        [
                            (x - 0) * TILE_SIZE - (car.road_pos + 1) * CAR_SIZE,
                            (y + 0) * TILE_SIZE + 0 * CAR_SIZE,
                        ],
                    )
                case Direction.RIGHT:
                    self._screen.blit(
                        pygame.transform.scale(self.car_right, (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 1) * TILE_SIZE + (car.road_pos) * CAR_SIZE,
                            (y + 0) * TILE_SIZE + 1 * CAR_SIZE,
                        ],
                    )

        print("###")

        pygame.display.update()
        pygame.display.flip()

        self._clock.tick(10)

    def is_running(self):
        return self._running
