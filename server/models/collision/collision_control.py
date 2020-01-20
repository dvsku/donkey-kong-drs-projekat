import multiprocessing as mp
from threading import Thread

from common.constants import SCENE_GRID_BLOCK_WIDTH, SCENE_GRID_BLOCK_HEIGHT, SCENE_WIDTH, SCENE_HEIGHT
from common.enums.climb_state import ClimbState
from common.enums.collision_control_methods import CCMethods
from common.enums.direction import Direction
from common.enums.layout_block import LayoutBlock
from server.models.collision.pipe_message import Message


class CollisionControl(mp.Process):

    def __init__(self, endpoint):
        mp.Process.__init__(self)

        self.server_endpoint = endpoint
        self.endpoints = []
        self.threads = []
        self.start()

    def add_endpoint(self, pipe_endpoint):
        self.endpoints.append(pipe_endpoint)
        index = self.endpoints.index(pipe_endpoint)

        thread = Thread(target=self.do_work, args=[index])
        thread.start()

    def do_work(self, index):
        while True:
            msg = self.endpoints[index].recv()
            if msg.func == "end":
                break
            self.dispatch(msg, index=index)

    def run(self):
        while True:
            msg = self.server_endpoint.recv()
            if msg.func == "end":
                break
            self.dispatch(msg)

    def dispatch(self, msg: Message, index=None):
        handler = getattr(self, msg.func, None)
        if handler:
            if index is None:
                handler(*msg.args)
            else:
                handler(index, *msg.args)

    def check_end_of_screen_left(self, index, x):
        ret_val = False

        if x <= 0:
            ret_val = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_falling(self, index, player_x, player_y, direction, layout):
        ret_value = False

        y = int((player_y + 35) / SCENE_GRID_BLOCK_HEIGHT)
        if direction == Direction.LEFT:
            x = int((player_x + 20) / SCENE_GRID_BLOCK_WIDTH)
        elif direction == Direction.RIGHT:
            x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
        else:
            return False

        if layout[y][x] is None:
            ret_value = True
        elif layout[y][x] == LayoutBlock.Platform or layout[y][x] == LayoutBlock.Ladder:
            if (y * SCENE_GRID_BLOCK_HEIGHT) > player_y + 35:
                ret_value = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_value))

    def check_climbing_up(self, index, player_x, player_y, layout):
        # default return value, if it's NONE, don't climb
        ret_value = ClimbState.NONE

        # get x center point
        player_x_center = player_x + 13

        # get x  of the block the player is in
        x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
        # get y of the block the player is in (feet level)
        y = int((player_y + 34) / SCENE_GRID_BLOCK_HEIGHT)

        if layout[y][x] == LayoutBlock.Ladder:
            # get climbable ladder x coordinates (the whole ladder is not climbable)
            ladder_x_from = x * SCENE_GRID_BLOCK_WIDTH + 5
            ladder_x_to = x * SCENE_GRID_BLOCK_WIDTH + 30

            # check if the player is between climbable x coordinates
            if (ladder_x_from < player_x_center) and (ladder_x_to > player_x_center):
                # get y of the block at player head level
                y = int((player_y + 3) / SCENE_GRID_BLOCK_HEIGHT)

                # check if block above the player's head is empty
                if layout[y][x] is None:
                    ret_value = ClimbState.FINISH
                else:
                    ret_value = ClimbState.CLIMB

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_value))

    def check_climbing_down(self, index, player_x, player_y, layout):
        # default return value, if it's NONE, don't climb
        ret_value = ClimbState.NONE

        # get x center point
        player_x_center = player_x + 13

        # get x  of the block the player is in
        x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
        # get y of the block the player is in (feet level)
        y = int((player_y + 35) / SCENE_GRID_BLOCK_HEIGHT)

        if layout[y][x] == LayoutBlock.Ladder:
            # get climbable ladder x coordinates (the whole ladder is not climbable)
            ladder_x_from = x * SCENE_GRID_BLOCK_WIDTH + 5
            ladder_x_to = x * SCENE_GRID_BLOCK_WIDTH + 30

            # check if the player is between climbable x coordinates
            if (ladder_x_from < player_x_center) and (ladder_x_to > player_x_center):
                # get y of the block at player head level
                y = int((player_y + 3) / SCENE_GRID_BLOCK_HEIGHT)

                # check if block above the player's head is empty
                if layout[y][x] is None:
                    ret_value = ClimbState.FINISH
                else:
                    ret_value = ClimbState.CLIMB

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_value))

    def check_end_of_screen_right(self, index, x):
        ret_val = False

        if x >= SCENE_WIDTH - 26:
            ret_val = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_end_of_screen_vertical(self, index, y):
        ret_val = False
        if y >= SCENE_HEIGHT - 60:
            ret_val = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_barrel_collision(self, index, b_x, b_y, p_x, p_y):
        ret_val = True

        barrel_pos_y_from = b_y
        barrel_pos_y_to = b_y + 29
        barrel_pos_x_from = b_x
        barrel_pos_x_to = barrel_pos_x_from + 29
        player_pos_y_from = p_y
        player_pos_y_to = p_y + 35
        player_pos_x_from = p_x
        player_pos_x_to = p_x + 26

        if ((barrel_pos_y_from < player_pos_y_from) and (barrel_pos_y_to < player_pos_y_from)) or (
                (barrel_pos_y_from > player_pos_y_to) and (barrel_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((barrel_pos_x_from < player_pos_x_from) and (barrel_pos_x_to < player_pos_x_from)) or \
                ((barrel_pos_x_from > player_pos_x_to) and (barrel_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_princess_collision(self, index, pr_x, pr_y, p_x, p_y):
        ret_val = True

        princess_pos_y_from = pr_y
        princess_pos_y_to = pr_y + 37
        princess_pos_x_from = pr_x
        princess_pos_x_to = pr_x + 34
        player_pos_y_from = p_y
        player_pos_y_to = p_y + 35
        player_pos_x_from = p_x
        player_pos_x_to = p_x + 26

        if ((princess_pos_y_from < player_pos_y_from) and (princess_pos_y_to < player_pos_y_from)) or (
                (princess_pos_y_from > player_pos_y_to) and (princess_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((princess_pos_x_from < player_pos_x_from) and (princess_pos_x_to < player_pos_x_from)) or (
                (princess_pos_x_from > player_pos_x_to) and (princess_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_coin_collision(self, index, c_x, c_y, p_x, p_y):
        ret_val = True

        coin_pos_y_from = c_y
        coin_pos_y_to = c_y + 40
        coin_pos_x_from = c_x
        coin_pos_x_to = c_x + 40
        player_pos_y_from = p_y
        player_pos_y_to = p_y + 35
        player_pos_x_from = p_x
        player_pos_x_to = p_x + 26

        if ((coin_pos_y_from < player_pos_y_from) and (coin_pos_y_to < player_pos_y_from)) or (
                (coin_pos_y_from > player_pos_y_to) and (coin_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((coin_pos_x_from < player_pos_x_from) and (coin_pos_x_to < player_pos_x_from)) or (
                (coin_pos_x_from > player_pos_x_to) and (coin_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_gorilla_collision(self, index, g_x, g_y, p_x, p_y):
        ret_val = True

        gorilla_y_from = g_y
        gorilla_pos_y_to = g_y + 55
        gorilla_pos_x_from = g_x
        gorilla_pos_x_to = g_x + 58
        player_pos_y_from = p_y
        player_pos_y_to = p_y + 35
        player_pos_x_from = p_x
        player_pos_x_to = p_x + 26

        if ((gorilla_y_from < player_pos_y_from) and (gorilla_pos_y_to < player_pos_y_from)) or (
                (gorilla_y_from > player_pos_y_to) and (gorilla_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((gorilla_pos_x_from < player_pos_x_from) and (gorilla_pos_x_to < player_pos_x_from)) or (
                (gorilla_pos_x_from > player_pos_x_to) and (gorilla_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))
