from unittest.mock import patch
import unittest

from psi_environment.environment import Environment, Map


class TestPoints(unittest.TestCase):
    def test_bot_not_collect_points_5_map(self):
        """
        Tests whether bot collects points using Map.step()
        """
        n_points = 5
        map = Map(n_points=n_points, random_seed=23, agent_type=None)
        for _ in range(100):
            map.step()

        self.assertEqual(n_points, len(map._map_state._points))
    
    def test_bot_not_collect_points_100000_map(self):
        """
        Tests whether bot collects points using Map.step() for more points and iterations
        """
        n_points = 100
        map = Map(n_points=n_points, random_seed=23, agent_type=None)
        for _ in range(100_000):
            map.step()

        self.assertEqual(n_points, len(map._map_state._points))

    def test_bot_not_collect_points_env(self):
        """
        Tests whether bot collects points using Environment.step()
        """
        n_points = 100
        env = Environment(
            agent_type=None,
            ticks_per_second=20,
            n_bots=100,
            n_points=n_points,
            random_seed=23,
        )
        for _ in range(1000):
            env.step()

        self.assertEqual(n_points, len(env._map._map_state._points))
