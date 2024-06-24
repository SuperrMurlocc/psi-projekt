from psi_environment.data.map_state import MapState, Road
from psi_environment.data.point import Point
import warnings
# Code readability improvements are not applicable in this section as no specific code block is provided to refactor or comment.


class TestPoints:
    def setup_method(self):
        self.random_seed = 2137
        self.map_state = MapState(random_seed=self.random_seed)  
        self.n_points = 10
        self.points = self.map_state.add_points(self.n_points)

    def test_add_points_correct_count(self):
        """
        Test if the number of points generated is correct
        """
        assert len(self.points) == self.n_points, (f"Number of points generated ({len(self.points)}) does not match the given number ({self.n_points})."
        )

    def test_add_points_valid_positions(self):
        '''
        Test if all points are on the roads
        '''
        point_positions = [point for point in self.points.values()]
        roads = self.map_state.get_road_tiles_map_positions()
        assert all(point in roads for point in point_positions), "All points are not on the roads."

    def test_add_points_non_negative_coordinates(self):
        """
        Test if all points have non-negative coordinates
        """
        for point_id, point in self.points.items():
            assert point[0] >= 0 and point[1] >= 0, f"Point {point_id} has negative coordintes: {point}."
    
    def test_add_points_unique_positions(self):
        """
        Test if all points have unique positions
        """
        positions = [point for point in self.points.values()]
        positions_unique = set(positions)
        assert len(positions) == len(positions_unique), "Duplicate points detected."

