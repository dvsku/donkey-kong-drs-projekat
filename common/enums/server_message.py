from enum import Enum


class ServerMessage(Enum):
    CONNECTION_ACK = 0
    LOAD_GAME_SCENE = 1
    LOAD_INFO_SCENE = 2
    MATCH_ENDED = 3
    MOVE = 4
    STOP = 5
    FALL = 6
    CLIMB_UP = 7
    CLIMB_DOWN = 8
    HIT = 9
    MOVE_OPPONENT = 10
    STOP_OPPONENT = 11
    FALL_OPPONENT = 12
    CLIMB_UP_OPPONENT = 13
    CLIMB_DOWN_OPPONENT = 14
    OPPONENT_HIT = 15
    DRAW_BARREL = 16
    REMOVE_BARREL = 17
    MOVE_BARREL = 18
    GORILLA_MOVE = 19
    GORILLA_THROW_BARREL = 20
    SET_POINTS = 21
    SET_POINTS_OPPONENT = 22