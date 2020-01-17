from enum import Enum


class CCMethods(Enum):
    END_OF_SCREEN_L = "check_end_of_screen_left"
    END_OF_SCREEN_R = "check_end_of_screen_right"
    END_OF_SCREEN_V = "check_end_of_screen_vertical"
    BARREL_COLLISION = "check_barrel_collision"
    FALLING = "check_falling"
    CLIMB_UP = "check_climbing_up"
    CLIMB_DOWN = "check_climbing_down"
    ADD_ENDPOINT = "add_endpoint"
    KILL_PROCESS = "end"
    EMPTY = ""
