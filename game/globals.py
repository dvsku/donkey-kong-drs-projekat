import os
from enum import Enum

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCENE_WIDTH = 800
SCENE_HEIGHT = 600
SCENE_GRID_BLOCK_WIDTH = 40
SCENE_GRID_BLOCK_HEIGHT = 40

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = ROOT_DIR + "/resources/"


class Direction(Enum):
    UP = 1
    DOWN = 2


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
