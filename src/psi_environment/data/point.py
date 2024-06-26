from enum import IntEnum


class PositionType(IntEnum):
    ROAD = 0
    NODE = 1


class Point:
    def __init__(
        self,
        map_position: tuple[int, int],
        road_positions: list[tuple[int, int]] | None = None,
        node: int | None = None,
    ):
        """Point class represents a point on the map. A point can be placed either on
        a road or on a node.

        Only one of road_positions and node_position can be set.

        Args:
            map_position (tuple[int, int]): map position of the point
            road_positions (list[tuple[int, int]] | None, optional): road positions of
                the point if the point is on a road. Defaults to None.
            node (int | None, optional): node where the point is if the point is on a
                node (duh). Defaults to None.

        Raises:
            ValueError: If both or none of road_positions and node_position are set
        """
        if road_positions is not None and node is not None:
            raise ValueError("Cannot have both road_positions and node_position")
        if road_positions is None and node is None:
            raise ValueError("Must have either road_positions or node_position")

        self.map_position = map_position
        self.type = (
            PositionType.ROAD if road_positions is not None else PositionType.NODE
        )
        self.road_positions = road_positions
        self.node = node

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.map_position}, {repr(self.type)})"
