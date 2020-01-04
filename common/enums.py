import os
from enum import Enum

COMMON_ROOT = os.path.dirname(os.path.abspath(__file__))


class ClientMessage(Enum):
    CONNECTION_ESTABLISHED = 0
    REQUEST_GAME = 1
    MOVE = 2
    STOP = 3
    POS = 4
    CLOSE = 9


class ServerMessage(Enum):
    CONNECTION_ACK = 0
    LOAD_SCENE = 1
    MOVE_OPPONENT = 2
    STOP_OPPONENT = 3
    FALL_OPPONENT = 4
    MOVE = 5
    STOP = 6
    FALL = 7
    DRAW_BARREL = 8
    REMOVE_BARREL = 9
    MOVE_BARREL = 10
    HIT = 11
    OPPONENT_HIT = 12
    MATCH_ENDED = 20


class MessageFormat(Enum):
    ONLY_COMMAND = '{{ "command" : {} }}'
    COMMAND_SCENE = '{{ "command" : {}, "scene" : {}, "player" : {} }}'
    COMMAND_MOVE = '{{ "command" : {}, "direction" : {}, "x" : {}, "y" : {} }}'
    COMMAND_POS = '{{ "command" : {}, "x" : {}, "y" : {} }}'
    COMMAND_DRAW_BARREL = '{{ "command" : {}, "x" : {}, "y" : {}, "index" : {} }}'
    COMMAND_REMOVE_BARREL = '{{ "command" : {}, "index" : {} }}'
    COMMAND_MOVE_BARREL = '{{ "command" : {}, "index" : {} }}'


class Scene(Enum):
    MAIN_MENU = 0
    WAITING_FOR_PLAYERS = 1
    FIRST_LEVEL = 2
    SECOND_LEVEL = 3
    THIRD_LEVEL = 4
    FOURTH_LEVEL = 5
    FIFTH_LEVEL = 6
    MATCH_END = 7


class Player(Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2


class LayoutBlock(Enum):
    Platform = 1
    Ladder = 2


class Layouts(Enum):
    FirstLevel = COMMON_ROOT + "/layouts/first_level_layout.txt"
