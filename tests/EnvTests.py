
import unittest
from unittest.mock import patch, Mock, MagicMock


import numpy.random
from psi_environment.data.action import Action
from psi_environment.environment import Environment
from psi_environment.data.car import Car
from psi_environment.data.car import DummyAgent


class TestEnvironment(unittest.TestCase):
    @patch('psi_environment.environment.Map')
    @patch('psi_environment.environment.Game')
    def test_environment_initialization_with_default_values(self, mock_game, mock_map):
        """
        Test if environment is initialized with default values
        """
        env = Environment()
        mock_map.assert_called_once()
        mock_game.assert_called_once()
        self.assertTrue(env.is_running())

    def test_environment_initialization_with_custom_values(self):
        """
         Test if environment is initialized with custom values
         """
        env = Environment(agent_type=Car, ticks_per_second=20, n_bots=5, n_points=2, traffic_lights_percentage=0.2, traffic_lights_length=5, random_seed=42)
        self.assertTrue(env.is_running())

    def test_environment_values_are_correct(self):
        env = Environment(agent_type=Car, ticks_per_second=20, n_bots=5, n_points=2, traffic_lights_percentage=0.2, traffic_lights_length=5, random_seed=42)
        self.assertEqual(env._random_seed, 42)
        self.assertEqual(env._map._random_seed, 42)
        self.assertEqual(env._game._random_seed, 42)

        botsAgents = [env._map._cars[key] for key in env._map._cars.keys() if isinstance(env._map._cars[key], DummyAgent)]
        self.assertEqual(len(botsAgents), 5)
        self.assertEqual(env._map.n_points, 2)
        self.assertEqual(len(env._map._map_state._traffic_lights), 6)
        self.assertEqual(env._map._traffic_lights_length, 5)
        self.assertEqual(env._game._ticks_per_second, 20)
        self.assertTrue(env.is_running())

    @patch('psi_environment.environment.Map')
    @patch('psi_environment.environment.Game')
    def test_environment_step_when_game_is_not_over(self, mock_game, mock_map):

        """
         Test environment step method when game is not over
         """
        mock_map.return_value.is_game_over.return_value = False
        env = Environment()
        timestep, is_running = env.step()
        mock_map.return_value.step.assert_called_once()
        mock_game.return_value.step.assert_called_once()
        self.assertEqual(timestep, mock_game.return_value.get_timestep.return_value)
        self.assertTrue(is_running)


    def test_environment_still_running_after_game_over(self):
        """
         Test if is_running() method return false after game stop
         """

        #mock_map.return_value.is_game_over.return_value = True
        env = Environment()
        env.step()
        env.step()
        self.assertTrue(env.is_running())
        env._game.stop()
        self.assertFalse(env.is_running())



    def test_environment_reset(self):
        """
        Tests if reset method resets the environment to the initial state
        """

        env = Environment()
        initial_state = env.__dict__.copy()
        env.step()
        env.step()
        env.step()
        env.step()
        self.assertTrue(env.is_running())
        self.assertTrue(env.is_running())
        try:
            env.reset()
            self.assertEqual(env.__dict__, initial_state)
        except:
            self.fail("Reset method not working")


    def test_spawn_point(self):
        """
        Tests if the spawn point is the same for the same seed
        :return:
        """
        env1 = Environment(n_bots=0, random_seed=0)
        env2 = Environment(n_bots=0, random_seed=0)

        pos1 = env1._map._cars[1]
        pos2 = env2._map._cars[1]

        self.assertEqual(pos1.__dict__, pos2.__dict__)


    def test_spawn_point_different_seed(self):
        """
        Tests if the spawn point is different for different seeds
        """
        env1 = Environment(n_bots=0, random_seed=0)
        env2 = Environment(n_bots=0, random_seed=1)

        pos1 = env1._map._cars[1]
        pos2 = env2._map._cars[1]

        self.assertNotEqual(pos1.__dict__, pos2.__dict__)

    def test_const_bot_movement(self, max_iter=100):
        """
        Tests if bot moves depends on seed
        """
        env1 = Environment(n_bots=0, random_seed=0)
        env2 = Environment(n_bots=0, random_seed=0)
        pos1 = []
        pos2 = []
        for i in range(max_iter):
            env1.step()
            env2.step()
            pos1.append(env1._map._cars[1].road_pos)
            pos2.append(env2._map._cars[1].road_pos)
        self.assertEqual(pos1, pos2)

    @patch('numpy.random.default_rng')
    #@patch('psi_environment.api.environment_api.EnvironmentAPI.is_position_road_end', return_value=False)
    # @patch('psi_environment.api.environment_api.EnvironmentAPI.get_available_turns', return_value=[Action.FORWARD,
    #                                                                                                Action.BACK,
    #                                                                                                Action.LEFT,
    #                                                                                                Action.RIGHT])
    #@patch('psi_environment.data.car.DummyAgent.rng.choice', return_value='XD')
    def test_bots2(self, env_api_mock):
        """tests if bots are not making the same moves"""

        mock_choice = MagicMock()
        def side_effect(*args, **kwargs):
            if args[0] == [Action.FORWARD, Action.BACK] and kwargs.get('p') == [0.95, 0.05]:
                return 2
            else:
                return numpy.random.choice(*args)

        mock_choice.side_effect = side_effect
        mock_choice.original_method = env_api_mock.return_value.choice
        env_api_mock.return_value.choice = mock_choice


        env1 = Environment(n_bots=4, random_seed=0)
        dict = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: []
        }
        for i in range(20):
            env1.step()
            #time.sleep(0.5)
            for k, car in enumerate(env1._map._cars):
                dict[k].append(env1._map._cars[car]._last_action)

        list_the_same = dict[0] == dict[1] == dict[2] == dict[3] == dict[4]
        self.assertFalse(list_the_same)

if __name__ == '__main__':
    unittest.main()