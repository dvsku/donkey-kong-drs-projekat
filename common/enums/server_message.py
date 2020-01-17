from enum import Enum


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
    CLIMB_UP = 13
    CLIMB_DOWN = 14
    CLIMB_UP_OPPONENT = 15
    CLIMB_DOWN_OPPONENT = 16
    MATCH_ENDED = 20
