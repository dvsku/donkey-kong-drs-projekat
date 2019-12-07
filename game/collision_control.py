import multiprocessing as mp
from game.globals import *
from game.models.helper.queue_message import Message


class CollisionControl(mp.Process):

    def __init__(self, recv_queue: mp.Queue, send_queue: mp.Queue):
        mp.Process.__init__(self)
        self.send_queue = send_queue
        self.recv_queue = recv_queue
        self.start()

    def run(self):
        while True:
            if not self.recv_queue.empty():
                msg = self.recv_queue.get()
                if msg.func == "end":
                    break

                self.dispatch(msg)

        self.send_queue.put(Message(CCMethods.EMPTY))

    def dispatch(self, msg: Message):
        handler = getattr(self, msg.func, None)
        if handler:
            handler(*msg.args)

    def check_end_of_screen_left(self, x):
        ret_val = False

        if x <= -5:
            ret_val = True

        self.send_queue.put(Message(CCMethods.EMPTY, ret_val))

    def check_end_of_screen_right(self, x):
        ret_val = False

        if x >= SCENE_WIDTH - 35:
            ret_val = True

        self.send_queue.put(Message(CCMethods.EMPTY, ret_val))

    def check_end_of_screen_vertical(self, y):
        ret_val = False
        if y >= SCENE_HEIGHT - 40:
            ret_val = True

        self.send_queue.put(Message(CCMethods.EMPTY, ret_val))

    def check_barrel_collision(self, b_x, b_y, b_width, p_x, p_y):
        ret_val = True

        barrel_pos_y = b_y
        barrel_pos_x_from = b_x
        barrel_pos_x_to = barrel_pos_x_from + b_width

        player_pos_y = p_y
        # player sprite is 40x40px but without transparent pixels the character is actually 22px wide
        player_pos_x_from = p_x + 9
        player_pos_x_to = p_x + 22

        if barrel_pos_y != player_pos_y:
            ret_val = False

        if ((barrel_pos_x_from < player_pos_x_from) and (barrel_pos_x_to < player_pos_x_from)) or \
                ((barrel_pos_x_from > player_pos_x_to) and (barrel_pos_x_to > player_pos_x_to)):
            ret_val = False

        self.send_queue.put(Message(CCMethods.EMPTY, ret_val))
