import multiprocessing as mp
from threading import Thread
from client.globals import *
from client.models.helper.pipe_message import Message
from common.enums import LayoutBlock


class CollisionControl(mp.Process):

    def __init__(self, endpoint):
        mp.Process.__init__(self)

        self.server_endpoint = endpoint
        self.endpoints = []
        self.threads = []

        # self.send_queue = send_queue
        # self.recv_queue = recv_queue
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

        barrel_pos_y = b_y
        barrel_pos_x_from = b_x
        barrel_pos_x_to = barrel_pos_x_from + 29

        player_pos_y = p_y
        player_pos_x_from = p_x
        player_pos_x_to = p_x + 26

        if barrel_pos_y <= player_pos_y:
            ret_val = False

        if ((barrel_pos_x_from < player_pos_x_from) and (barrel_pos_x_to < player_pos_x_from)) or \
                ((barrel_pos_x_from > player_pos_x_to) and (barrel_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))
