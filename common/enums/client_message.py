from enum import Enum


class ClientMessage(Enum):
    CONNECTION_ESTABLISHED = 0
    REQUEST_GAME = 1
    MOVE = 2
    STOP = 3
    POS = 4
    CLOSE = 9
    READY = 10
