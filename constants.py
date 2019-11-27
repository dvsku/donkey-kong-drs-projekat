from enum import Enum

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCENE_WIDTH = 800
SCENE_HEIGHT = 600
SCENE_GRID_BLOCK_WIDTH = 40
SCENE_GRID_BLOCK_HEIGHT = 40


class Direction(Enum):
    UP = 1
    DOWN = 2


class State(Enum):
    NONE = 0
    NORMAL = 1
    HIGHLIGHTED = 2
