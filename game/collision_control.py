import multiprocessing as mp
from threading import Thread
from game.globals import *
from game.models.helper.queue_message import Message


class CollisionControl(mp.Process):
    def __init__(self, game_endpoint):
        mp.Process.__init__(self)
        self.game_endpoint = game_endpoint
        self.endpoints = []
        self.endpoint_threads = []
        self.start()

    def run(self):
        while True:
            try:
                msg = self.game_endpoint.recv()
                self.dispatch(msg)
            except BrokenPipeError:
                break
            except EOFError:
                break

    def do_work(self, index):
        while True:
            try:
                msg = self.endpoints[index].recv()
                self.dispatch(msg, index=index)
            except BrokenPipeError:
                break
            except EOFError:
                break

    def add_endpoint(self, pipe_endpoint):
        self.endpoints.append(pipe_endpoint)
        index = self.endpoints.index(pipe_endpoint)
        thread = Thread(target=self.do_work, args=[index])
        thread.start()

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

    def check_end_of_screen_right(self, index, x):
        ret_val = False

        if x >= SCENE_WIDTH - 26:
            ret_val = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_end_of_screen_vertical(self, index, y):
        ret_val = False
        if y >= SCENE_HEIGHT - 40:
            ret_val = True

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_barrel_collision(self, index, b_x, b_y, b_width, b_height, p_x, p_y, p_width, p_height):
        ret_val = True

        barrel_pos_y_from = b_y
        barrel_pos_y_to = b_y + b_height
        barrel_pos_x_from = b_x
        barrel_pos_x_to = barrel_pos_x_from + b_width
        player_pos_y_from = p_y
        player_pos_y_to = p_y + p_height
        player_pos_x_from = p_x
        player_pos_x_to = p_x + p_width

        if ((barrel_pos_y_from < player_pos_y_from) and (barrel_pos_y_to < player_pos_y_from)) or \
                ((barrel_pos_y_from > player_pos_y_to) and (barrel_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((barrel_pos_x_from < player_pos_x_from) and (barrel_pos_x_to < player_pos_x_from)) or \
                ((barrel_pos_x_from > player_pos_x_to) and (barrel_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_princess_collision(self, index, pr_x, pr_y, pr_width, pr_height, p_x, p_y, p_width, p_height):
        ret_val = True

        princess_pos_y_from = pr_y
        princess_pos_y_to = pr_y + pr_height
        princess_pos_x_from = pr_x
        princess_pos_x_to = pr_x + pr_width
        player_pos_y_from = p_y
        player_pos_y_to = p_y + p_height
        player_pos_x_from = p_x
        player_pos_x_to = p_x + p_width

        if ((princess_pos_y_from < player_pos_y_from) and (princess_pos_y_to < player_pos_y_from)) or \
                ((princess_pos_y_from > player_pos_y_to) and (princess_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((princess_pos_x_from < player_pos_x_from) and (princess_pos_x_to < player_pos_x_from)) or \
                ((princess_pos_x_from > player_pos_x_to) and (princess_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))

    def check_gorilla_collision(self, index, g_x, g_y, g_width, g_height, p_x, p_y, p_width, p_height):
        ret_val = True

        gorilla_pos_y_from = g_y
        gorilla_pos_y_to = g_y + g_height
        gorilla_pos_x_from = g_x
        gorilla_pos_x_to = g_x + g_width
        player_pos_y_from = p_y
        player_pos_y_to = p_y + p_height
        player_pos_x_from = p_x
        player_pos_x_to = p_x + p_width

        if ((gorilla_pos_y_from < player_pos_y_from) and (gorilla_pos_y_to < player_pos_y_from)) or \
                ((gorilla_pos_y_from > player_pos_y_to) and (gorilla_pos_y_to > player_pos_y_to)):
            ret_val = False

        if ((gorilla_pos_x_from < player_pos_x_from) and (gorilla_pos_x_to < player_pos_x_from)) or \
                ((gorilla_pos_x_from > player_pos_x_to) and (gorilla_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.endpoints[index].send(Message(CCMethods.EMPTY, ret_val))
