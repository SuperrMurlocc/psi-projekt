from typing import Any
import random
import pygame
import importlib.resources
from psi_environment.data.map import Map
from enum import IntEnum


PRE_COLOR = [
    (128, 0, 0),  # maroon
    (139, 0, 0),  # dark red
    (220, 20, 60),  # crimson
    (255, 99, 71),  # tomato
    (255, 215, 0),  # gold
    (128, 128, 0),  # olive
    (0, 128, 0),  # green
    (0, 255, 0),  # lime
    (0, 128, 128),  # teal
    (0, 255, 255),  # aqua
    (0, 0, 128),  # navy
    (0, 0, 255),  # blue
    (128, 0, 128),  # purple
    (255, 0, 255),  # magenta / fuchsia
    (255, 105, 180),  # hot pink
]


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Particle:
    def __init__(self, pos, direction, color, lifespan):
        self.pos = pos
        self.direction = direction
        self.color = color
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        self.age += 1
        if self.age < self.lifespan:
            self.pos[0] += self.direction[0]
            self.pos[1] += self.direction[1]
            alpha = int((1 - self.age / self.lifespan) * 255)
            self.color = (self.color[0], self.color[1], self.color[2], alpha)
        else:
            self.color = (self.color[0], self.color[1], self.color[2], 0)

    def is_alive(self):
        return self.age < self.lifespan


class Game:
    def __init__(self, map: Map, random_seed: int = None, ticks_per_second: int = 10):
        self._random_seed = random_seed
        self._timestep = 0
        self._map = map
        self._crossroads = map.get_map_state().get_map_array()
        
        pygame.init()
        pygame.display.set_caption("Traffic simulation")
        self.aspect_ratio = 1280 / 720
        self._screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.tile_size = 1280 // 30
        self.car_size = self.tile_size // 2
        self._clock = pygame.time.Clock()
        self._ticks_per_second = ticks_per_second
        self._running = True
        self._agents = self._map._agents
        self.particles = []
        self._init_images()
        self._crossroads_positions = dict()
        cros_id = 0
        for idy, y in enumerate(self._crossroads):
            for idx, x in enumerate(y):
                if x == "x":
                    self._crossroads_positions[cros_id] = [
                        idx * self.tile_size,
                        idy * self.tile_size,
                    ]
                    cros_id += 1

    def _init_images(self):
        # road tiles
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

        # env  tiles
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

        # car tiles
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

        # additional tiles
        with importlib.resources.path(
            "psi_environment.game.resources", "star.png"
        ) as star_path:
            self.star = pygame.image.load(str(star_path))

        self.colored_cars = {}
        self.create_colored_cars(self._agents.keys())
        
        self.colored_stars = {}
        self.create_colored_stars(self._agents.keys())

        self.env_tiles = [
            self.grass_flower_yellow,
            self.grass_flower,
            self.grass_hay,
            self.grass_hay2,
            self.grass_no_stalk,
            self.brick_tile,
        ]

        self.map_seed = self._map._random_seed


    def update_particles(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def create_particles(self, car_pos, direction, color):
        for _ in range(5):  # Create 5 particles per update
            offset = [random.randint(-5, 5), random.randint(-5, 5)]
            particle_pos = [car_pos[0] + self.car_size // 2 + offset[0], car_pos[1] + self.car_size // 2 + offset[1]]
            particle_direction = [direction[0] * random.uniform(0.5, 1.5), direction[1] * random.uniform(0.5, 1.5)]
            particle_color = color
            lifespan = random.randint(3, 10)  # Lifespan between 20 and 40 frames
            self.particles.append(Particle(particle_pos, particle_direction, particle_color, lifespan))


    def __del__(self):
        pygame.quit()

    def step(self):
        self._timestep += 1
        self.update_particles()
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
            color1[3],
        )
        return blended_color

    def change_color(self, image, new_color, blend_factor):
        new_image = image.copy()
        new_image.lock()
        width, height = new_image.get_size()

        for x in range(width):
            for y in range(height):
                pixel_color = new_image.get_at((x, y))

                if pixel_color.a != 0:
                    blended_color = self.blend_colors(
                        pixel_color, new_color, blend_factor
                    )
                    new_image.set_at((x, y), blended_color)

        new_image.unlock()
        return new_image

    def create_colored_cars(self, agent_car_list):
        BLEND_RATE = 0.7
        for car_id in agent_car_list:
            new_color = PRE_COLOR[car_id % len(PRE_COLOR)]
            self.colored_cars[car_id] = {
                Direction.UP: self.change_color(self.car_up, new_color, BLEND_RATE),
                Direction.DOWN: self.change_color(self.car_down, new_color, BLEND_RATE),
                Direction.LEFT: self.change_color(self.car_left, new_color, BLEND_RATE),
                Direction.RIGHT: self.change_color(
                    self.car_right, new_color, BLEND_RATE
                ),
            } 
   
    def create_colored_stars(self, agent_car_list):
        BLEND_RATE = 0.7
        for car_id in agent_car_list:
            new_color = PRE_COLOR[car_id % len(PRE_COLOR)]
            self.colored_stars[car_id] = self.change_color(self.star, new_color, BLEND_RATE)


    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                new_width = event.w
                new_height = int(new_width / self.aspect_ratio)
                self.tile_size = new_width // 30
                self.car_size = self.tile_size // 2
                self._screen = pygame.display.set_mode(
                    (new_width, new_height), pygame.RESIZABLE
                )
                cros_id = 0
                for idy, y in enumerate(self._crossroads):
                    for idx, x in enumerate(y):
                        if x == "x":
                            self._crossroads_positions[cros_id] = [
                                idx * self.tile_size,
                                idy * self.tile_size,
                            ]
                            cros_id += 1

        self._screen.fill((115,116,27))
        pygame.font.init()
        my_font = pygame.font.SysFont("Comic Sans MS", 10)
        count = 0
        for idy, y in enumerate(self._crossroads):
            for idx, x in enumerate(y):
                if x == "x":
                    self.crossroad = pygame.transform.scale(
                        self.crossroad, (self.tile_size, self.tile_size)
                    )
                    text_surface = my_font.render(f"{count}", False, (255, 255, 255))
                    count += 1
                    self._screen.blit(
                        self.crossroad, [idx * self.tile_size, idy * self.tile_size]
                    )
                    self._screen.blit(
                        text_surface, [idx * self.tile_size, idy * self.tile_size]
                    )

                elif x == "=":
                    self.road_hori = pygame.transform.scale(
                        self.road_hori, (self.tile_size, self.tile_size)
                    )
                    self._screen.blit(
                        self.road_hori, [idx * self.tile_size, idy * self.tile_size]
                    )
                elif x == "|":
                    self.road_vert = pygame.transform.scale(
                        self.road_vert, (self.tile_size, self.tile_size)
                    )
                    self._screen.blit(
                        self.road_vert, [idx * self.tile_size, idy * self.tile_size]
                    )
                elif x == "#":
                    tile = self.env_tiles[
                        (self.map_seed + (idx * idy + 1)) % len(self.env_tiles)
                    ]
                    tile = pygame.transform.scale(
                        tile, (self.tile_size, self.tile_size)
                    )
                    self._screen.blit(
                        tile, [idx * self.tile_size, idy * self.tile_size]
                    )

        cross_lights = self._map._map_state.get_traffic_lights()
        cross_lights = cross_lights.items()

        lights_radius = self.tile_size // 6
        lights_offset = self.tile_size // 2 - lights_radius

        CIRCLE_COLOR_RED = (255, 0, 0)
        CIRCLE_COLOR_GREEN = (0, 255, 0)

        for cross, light in cross_lights:
            cross_pos = self._crossroads_positions[cross]
            if (
                light._blocked_direction == Direction.UP
                or light._blocked_direction == Direction.DOWN
            ):
                if light._up_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_RED,
                        (
                            cross_pos[0] + self.tile_size // 2,
                            cross_pos[1] + self.tile_size // 2 - lights_offset,
                        ),
                        lights_radius,
                    )
                if light._down_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_RED,
                        (
                            cross_pos[0] + self.tile_size // 2,
                            cross_pos[1] + self.tile_size // 2 + lights_offset,
                        ),
                        lights_radius,
                    )
                if light._left_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_GREEN,
                        (
                            cross_pos[0] + self.tile_size // 2 - lights_offset,
                            cross_pos[1] + self.tile_size // 2,
                        ),
                        lights_radius,
                    )
                if light._right_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_GREEN,
                        (
                            cross_pos[0] + self.tile_size // 2 + lights_offset,
                            cross_pos[1] + self.tile_size // 2,
                        ),
                        lights_radius,
                    )
            if (
                light._blocked_direction == Direction.LEFT
                or light._blocked_direction == Direction.RIGHT
            ):
                if light._up_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_GREEN,
                        (
                            cross_pos[0] + self.tile_size // 2,
                            cross_pos[1] + self.tile_size // 2 - lights_offset,
                        ),
                        lights_radius,
                    )
                if light._down_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_GREEN,
                        (
                            cross_pos[0] + self.tile_size // 2,
                            cross_pos[1] + self.tile_size // 2 + lights_offset,
                        ),
                        lights_radius,
                    )
                if light._left_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_RED,
                        (
                            cross_pos[0] + self.tile_size // 2 - lights_offset,
                            cross_pos[1] + self.tile_size // 2,
                        ),
                        lights_radius,
                    )
                if light._right_node is not None:
                    pygame.draw.circle(
                        self._screen,
                        CIRCLE_COLOR_RED,
                        (
                            cross_pos[0] + self.tile_size // 2 + lights_offset,
                            cross_pos[1] + self.tile_size // 2,
                        ),
                        lights_radius,
                    )
                    
        for car_id, agent_points in zip(self._map._map_state._points ,self._map._map_state._points.values()):
            colored_star = self.colored_stars[car_id]
            for point_id, point in enumerate(agent_points):
                (x, y) = point.map_position
                self._screen.blit(
                    pygame.transform.scale(colored_star, (self.tile_size, self.tile_size)),
                    [x * self.tile_size, y * self.tile_size],
                )  
                text_surface = my_font.render(f"{point_id}", False, (0, 0, 0))
                self._screen.blit(text_surface, [x * self.tile_size + self.tile_size // 2.2, y * self.tile_size + self.tile_size // 2.3])

        for car in self._map._cars.values():
            pos = self._map._map_state._node_indices[car.get_road_key()[0]]
            direction = self._map._map_state._edges[car.get_road_key()]
            x, y = pos

            if car._car_id in self.colored_cars:
                car_images = self.colored_cars[car._car_id]
            else:
                car_images = {
                    Direction.UP: self.car_up,
                    Direction.DOWN: self.car_down,
                    Direction.LEFT: self.car_left,
                    Direction.RIGHT: self.car_right,
                }

            match direction:
                case Direction.UP:
                    car_pos =[
                        (x + 0) * self.tile_size + 1 * self.car_size,
                        (y - 1) * self.tile_size
                        - (car.get_road_pos() - 1) * self.car_size,
                    ]
                    self._screen.blit(
                        pygame.transform.scale(
                            car_images[Direction.UP], (self.car_size, self.car_size)
                        ),
                        car_pos
                    )
                    if car._car_id in self._map._agents:
                        self.create_particles(car_pos, [0, -1], PRE_COLOR[car._car_id % len(PRE_COLOR)])
                        
                case Direction.DOWN:
                    car_pos = [
                        (x + 0) * self.tile_size + 0 * self.car_size,
                        (y + 1) * self.tile_size
                        + (car.get_road_pos()) * self.car_size,
                    ]
                    self._screen.blit(
                        pygame.transform.scale(
                            car_images[Direction.DOWN], (self.car_size, self.car_size)
                        ),
                        car_pos
                    )
                    if car._car_id in self._map._agents:
                        self.create_particles(car_pos, [0, 1], PRE_COLOR[car._car_id % len(PRE_COLOR)])
                    
                case Direction.LEFT:
                    car_pos = [
                            (x - 0) * self.tile_size
                            - (car.get_road_pos() + 1) * self.car_size,
                            (y + 0) * self.tile_size + 0 * self.car_size,
                        ]
                    self._screen.blit(
                        pygame.transform.scale(
                            car_images[Direction.LEFT], (self.car_size, self.car_size)
                        ),
                        car_pos
                    )
                    if car._car_id in self._map._agents:
                        self.create_particles(car_pos, [-1, 0], PRE_COLOR[car._car_id % len(PRE_COLOR)])
                        
                case Direction.RIGHT:
                    car_pos = [
                            (x + 1) * self.tile_size
                            + (car.get_road_pos()) * self.car_size,
                            (y + 0) * self.tile_size + 1 * self.car_size,
                        ]
                    self._screen.blit(
                        pygame.transform.scale(
                            car_images[Direction.RIGHT], (self.car_size, self.car_size)
                        ),
                        car_pos
                    )
                    if car._car_id in self._map._agents:
                        self.create_particles(car_pos, [1, 0], PRE_COLOR[car._car_id % len(PRE_COLOR)])

        for particle in self.particles:
            if particle.is_alive():
                s = pygame.Surface((self.car_size // 8, self.car_size // 8), pygame.SRCALPHA)
                s.fill(particle.color)
                self._screen.blit(s, particle.pos)


        pygame.display.update()
        pygame.display.flip()

        self._clock.tick(self._ticks_per_second)

    def is_running(self):
        return self._running
