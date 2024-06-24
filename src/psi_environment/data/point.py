class Point:
    def __init__(self, map_position: tuple[int, int]):
        self.map_position = map_position

    def __repr__(self) -> str:
        return f"Point({self.map_position})"
