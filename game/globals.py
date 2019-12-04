import os
from enum import Enum

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCENE_WIDTH = 800
SCENE_HEIGHT = 600
SCENE_GRID_BLOCK_WIDTH = 40
SCENE_GRID_BLOCK_HEIGHT = 40

PLAYER_MOVE_SPEED_HORIZONTAL = 7

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = ROOT_DIR + "/resources/"


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class State(Enum):
    NONE = 0
    NORMAL = 1
    HIGHLIGHTED = 2


class PaintDirection(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class PaintObject(Enum):
    PLATFORM = 1
    STAIRS = 2
    PRINCESS = 3
    PLAYER_1 = 4
    PLAYER_2 = 5


class Player(Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2


def set_common_data(list1, list2):
    result = False
    for x in list1:
        for y in list2:
            if x == y:
                result = True
                return result

    return result
