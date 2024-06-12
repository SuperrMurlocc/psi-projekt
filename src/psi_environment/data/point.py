class Point:
    def __init__(self, map_position: tuple[int, int], point_id: int):
        self.map_position = map_position
        self.point_id = point_id

    def __repr__(self) -> str:
        return f"Point({self.map_position}, {self.point_id})"
