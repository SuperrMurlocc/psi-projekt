from enum import Enum


class StopMode(Enum):
    """The StopMode enum defines when the environment stop simulation

    ALL_FINISHED - check if every car collected every point
    ONE_FINISHED - check if at least one car collected every point
    """
    ALL_FINISHED = 0
    ONE_FINISHED = 1
