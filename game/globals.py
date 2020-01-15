import os
from enum import Enum

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

SCENE_WIDTH = 800
SCENE_HEIGHT = 600
SCENE_GRID_BLOCK_WIDTH = 40
SCENE_GRID_BLOCK_HEIGHT = 40

BARREL_POOL_SIZE = 5

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = ROOT_DIR + "/resources/images/"


class CCMethods(Enum):
    END_OF_SCREEN_L = "check_end_of_screen_left"
    END_OF_SCREEN_R = "check_end_of_screen_right"
    END_OF_SCREEN_V = "check_end_of_screen_vertical"
    BARREL_COLLISION = "check_barrel_collision"
    PRINCESS_COLLISION = "check_princess_collision"
    GORILLA_COLLISION = "check_gorilla_collision"
    KILL_PROCESS = "end"
    EMPTY = ""


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
    LADDER = 2
    PRINCESS = 3
    PLAYER_1 = 4
    PLAYER_2 = 5
    HELP_SIGN = 6
    LIVES = 7
    GORILLA = 8


class ClimbState(Enum):
    NONE = 0
    CLIMB = 1
    FINISH = 2
    START = 3
