from typing import Any
import random
import pygame
import importlib.resources
from psi_environment.data.map import Map
from enum import IntEnum

TILE_SIZE = 64
CAR_SIZE = 32

PRE_COLOR = [
    (128, 0, 0),   # maroon
    (139, 0, 0),   # dark red
    (220, 20, 60), # crimson
    (255, 99, 71), # tomato
    (255, 215, 0), # gold
    (128, 128, 0), # olive
    (0, 128, 0),   # green
    (0, 255, 0),   # lime
    (0, 128, 128), # teal
    (0, 255, 255), # aqua
    (0, 0, 128),   # navy
    (0, 0, 255),   # blue
    (128, 0, 128), # purple
    (255, 0, 255), # magenta / fuchsia
    (255, 105, 180) # hot pink
]


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3



class Game:
    def __init__(self, map: Map, random_seed: int = None, ticks_per_second: int = 10):
        self._random_seed = random_seed
        self._timestep = 0
        self._map = map
        self._crossroads = map.get_map_state().get_map_array()
        pygame.init()
        pygame.display.set_caption("Traffic simulation")
        self._screen = pygame.display.set_mode((1920, 1024))
        self._clock = pygame.time.Clock()
        self._ticks_per_second = ticks_per_second
        self._running = True
        self._init_images()
        # no crossroad tile yet

    def _init_images(self):
        #road tiles
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
        
        #env  tiles
        with importlib.resources.path(
            "psi_environment.game.resources", "grass_flower_yellow.png"
        ) as grass_flower_yellow_path:
            self.grass_flower_yellow = pygame.image.load(str(grass_flower_yellow_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "grass_flower.png"
        ) as grass_flower_path:
            self.grass_flower = pygame.image.load(str(grass_flower_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "grass_hay.png"
        ) as grass_hay_path:
            self.grass_hay = pygame.image.load(str(grass_hay_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "grass_hay_2.png"
        ) as grass_hay2_path:
            self.grass_hay2 = pygame.image.load(str(grass_hay2_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "grass_no_stalk.png"
        ) as grass_no_stalk_path:
            self.grass_no_stalk = pygame.image.load(str(grass_no_stalk_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "brick_tile.png"
        ) as gbrick_tile_path:
            self.brick_tile = pygame.image.load(str(gbrick_tile_path))
        
        #car tiles
        with importlib.resources.path(
            "psi_environment.game.resources", "car_left_white.png"
        ) as car_left_path:
            self.car_left = pygame.image.load(str(car_left_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_right_white.png"
        ) as car_right_path:
            self.car_right = pygame.image.load(str(car_right_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_up_white.png"
        ) as car_up_path:
            self.car_up = pygame.image.load(str(car_up_path))
        with importlib.resources.path(
            "psi_environment.game.resources", "car_down_white.png"
        ) as car_down_path:
            self.car_down = pygame.image.load(str(car_down_path))

        #additional tiles
        with importlib.resources.path(
            "psi_environment.game.resources", "star.png"
        ) as star_path:
            self.star = pygame.image.load(str(star_path))

        self.colored_cars = {}
        self.create_colored_cars([1,2,3,6])

        self.env_tiles = [
            self.grass_flower_yellow,
            self.grass_flower,
            self.grass_hay,
            self.grass_hay2,
            self.grass_no_stalk,
            self.brick_tile
        ]
        
        self.map_seed = self._map._random_seed
            

    def __del__(self):
        pygame.quit()

    def step(self):
        self._timestep += 1
        self.render()
        self.is_running()

    def get_timestep(self) -> int:
        return self._timestep

    def reset(self):
        raise NotImplementedError

    def stop(self):
        self._running = False
        pygame.quit()

    def blend_colors(self, color1, color2, blend_factor):
        blended_color = (
            int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor),
            int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor),
            int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor),
            color1[3]
        )
        return blended_color

    def change_car_color(self, image, new_color, blend_factor):
        new_image = image.copy()
        new_image.lock()
        width, height = new_image.get_size()

        for x in range(width):
            for y in range(height):
                pixel_color = new_image.get_at((x, y))
                
                if pixel_color.a != 0:
                    blended_color = self.blend_colors(pixel_color, new_color, blend_factor)
                    new_image.set_at((x, y), blended_color)
        
        new_image.unlock()
        return new_image

    def create_colored_cars(self, agent_car_list):
        BLEND_RATE = 0.7
        for car_id in agent_car_list:
            new_color = PRE_COLOR[car_id%len(PRE_COLOR)]
            self.colored_cars[car_id] = {
                Direction.UP: self.change_car_color(self.car_up, new_color, BLEND_RATE),
                Direction.DOWN: self.change_car_color(self.car_down, new_color, BLEND_RATE),
                Direction.LEFT: self.change_car_color(self.car_left, new_color, BLEND_RATE),
                Direction.RIGHT: self.change_car_color(self.car_right, new_color, BLEND_RATE)
            }

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

        self._screen.fill("black")
        pygame.font.init()
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
                    self._screen.blit(
                        self.crossroad, [idx * TILE_SIZE, idy * TILE_SIZE]
                    )
                    self._screen.blit(text_surface, [idx * TILE_SIZE, idy * TILE_SIZE])

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
                    tile = self.env_tiles[(self.map_seed+(idx*idy+1))%len(self.env_tiles)]
                    tile = pygame.transform.scale(
                        tile, (TILE_SIZE, TILE_SIZE)
                    )
                    self._screen.blit(tile, [idx * TILE_SIZE, idy * TILE_SIZE])

        for point in self._map._map_state._points.values():
            x, y = point[0], point[1]
            self._screen.blit(
                pygame.transform.scale(self.star, (TILE_SIZE, TILE_SIZE)),
                [x * TILE_SIZE, y * TILE_SIZE],
            )

        for car in self._map._cars.values():
            pos = self._map._map_state._node_indices[car.road_key[0]]
            direction = self._map._map_state._edges[car.road_key]
            x, y = pos

            if car._car_id in self.colored_cars:
                car_images = self.colored_cars[car._car_id]
            else:
                car_images = {
                    Direction.UP: self.car_up,
                    Direction.DOWN: self.car_down,
                    Direction.LEFT: self.car_left,
                    Direction.RIGHT: self.car_right
                }

            match direction:
                case Direction.UP:
                    self._screen.blit(
                        pygame.transform.scale(car_images[Direction.UP], (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 0) * TILE_SIZE + 1 * CAR_SIZE,
                            (y - 1) * TILE_SIZE - (car.road_pos - 1) * CAR_SIZE,
                        ],
                    )
                case Direction.DOWN:
                    self._screen.blit(
                        pygame.transform.scale(car_images[Direction.DOWN], (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 0) * TILE_SIZE + 0 * CAR_SIZE,
                            (y + 1) * TILE_SIZE + (car.road_pos) * CAR_SIZE,
                        ],
                    )
                case Direction.LEFT:
                    self._screen.blit(
                        pygame.transform.scale(car_images[Direction.LEFT], (CAR_SIZE, CAR_SIZE)),
                        [
                            (x - 0) * TILE_SIZE - (car.road_pos + 1) * CAR_SIZE,
                            (y + 0) * TILE_SIZE + 0 * CAR_SIZE,
                        ],
                    )
                case Direction.RIGHT:
                    self._screen.blit(
                        pygame.transform.scale(car_images[Direction.RIGHT], (CAR_SIZE, CAR_SIZE)),
                        [
                            (x + 1) * TILE_SIZE + (car.road_pos) * CAR_SIZE,
                            (y + 0) * TILE_SIZE + 1 * CAR_SIZE,
                        ],
                    )

        pygame.display.update()
        pygame.display.flip()

        self._clock.tick(self._ticks_per_second)

    def is_running(self):
        return self._running
