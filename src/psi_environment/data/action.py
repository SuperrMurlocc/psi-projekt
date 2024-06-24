from enum import IntEnum


class Action(IntEnum):
    """The Action enum represents possible actions that can be taken within the 
    environment. Each action corresponds to a specific direction of movement.
    """
    RIGHT = 1
    FORWARD = 2
    LEFT = 3
    BACK = 4
