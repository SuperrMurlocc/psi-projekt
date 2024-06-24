class Point:
    """The Point class represents a point on the map that can be collected by cars.
    Each point has a unique identifier and a position on the map.
    """

    def __init__(self, map_position: tuple[int, int]):
        """Initializes the Point instance.

        Args:
            map_position (tuple[int, int]): The (x, y) coordinates of the point on
                the map.
        """
        self.map_position = map_position

    def __repr__(self) -> str:
        return f"Point({self.map_position})"
