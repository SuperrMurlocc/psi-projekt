import unittest
from unittest.mock import patch, Mock, MagicMock
import numpy.random
from psi_environment.data.action import Action
from psi_environment.environment import Environment
from psi_environment.data.car import Car
from psi_environment.data.car import DummyAgent
from psi_environment.data.map_state import MapState


def return_road_end(map_state, road_key):
    return map_state.get_road(road_key).length - 1

class TestTraffic(unittest.TestCase):

    def test_two_cars_both_forward_no_coll(self):
        """
        Tests if two cars move forward without collision
        """

        map_state = MapState(0, traffic_light_percentage=0)

        actions = [(1, Action.FORWARD, True),
                   (2, Action.FORWARD, False)]

        map_state._cars = {
            1: ((6, 7), return_road_end(map_state, (6, 7))),
            2: ((8, 7), return_road_end(map_state, (8, 7))),
        }

        map_state.move_cars(actions)

        expected_result = {1: ((7, 8), 0), 2: ((7, 6), 0)}
        self.assertEqual(expected_result, map_state._cars)

        map_state._cars = {
            1: ((1, 7), return_road_end(map_state, (1, 7))),
            2: ((13, 7), return_road_end(map_state, (13, 7))),
        }

        map_state.move_cars(actions)
        expected_result = {1: ((7, 13), 0), 2: ((7, 1), 0)}
        self.assertEqual(expected_result, map_state._cars)




    def test_two_cars_no_coll(self):
        map_state = MapState(0, traffic_light_percentage=0)

        actions = [(1, Action.RIGHT, True),
                   (2, Action.FORWARD, False)]

        #case 1
        map_state._cars = {
            1: ((13, 7), return_road_end(map_state, (13, 7))),
            2: ((1, 7), return_road_end(map_state, (1, 7))),
        }
        map_state.move_cars(actions)
        expected_result = {1: ((7, 8), 0), 2: ((7, 13), 0)}
        self.assertEqual(expected_result, map_state._cars)

        #case 2
        map_state._cars = {
            1: ((8, 7), return_road_end(map_state, (8, 7))),
            2: ((1, 7), return_road_end(map_state, (1, 7))),
        }
        map_state.move_cars(actions)
        expected_result = {1: ((7, 1), 0), 2: ((7, 13), 0)}
        self.assertEqual(expected_result, map_state._cars)


        # case 3
        map_state._cars = {
            1: ((1, 7), return_road_end(map_state, (1, 7))),
            2: ((13, 7), return_road_end(map_state, (13, 7))),
        }
        map_state.move_cars(actions)
        expected_result = {1: ((7, 6), 0), 2: ((7, 1), 0)}
        self.assertEqual(expected_result, map_state._cars)


        # case 4
        map_state._cars = {
            1: ((6, 7), return_road_end(map_state, (6, 7))),
            2: ((13, 7), return_road_end(map_state, (13, 7))),
        }
        map_state.move_cars(actions)
        expected_result = {1: ((7, 13), 0), 2: ((7, 1), 0)}
        self.assertEqual(expected_result, map_state._cars)




