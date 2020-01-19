import socket
from threading import Thread
from common.constants import PLAYER_LIVES


class Client:
    def __init__(self, parent: 'Server', client_socket=None):
        self.__parent__ = parent
        self.kill_thread = False
        self.starting_x = None
        self.starting_y = None
        self.x = None
        self.y = None
        self.lives = PLAYER_LIVES
        self.latest_direction = None
        self.falling = False
        self.ready = False
        self.climbing = False
        self.highest_y = 600
        self.points = 0
        self.socket = client_socket
        self.socket.settimeout(2)
        self.thread = Thread(target=self.__do_work)
        self.thread.start()

    def send(self, msg):
        try:
            self.socket.send(bytes(msg, 'utf-8'))
        except OSError:
            self.__parent__.stop_match(self)

    def add_point(self):
        if self.highest_y > self.y:
            self.points += 1
            self.highest_y = self.y

    def close(self):
        self.socket.close()
        self.kill_thread = True

    def lose_life(self):
        self.lives -= 1

    def set_coordinates(self, x, y):
        self.x = x
        self.y = y

    def __do_work(self):
        while True:
            try:
                if self.__parent__.kill_thread or self.kill_thread:
                    break
                msg = self.socket.recv(1024)
            except socket.error as e:
                if e.args[0] != "timed out":
                    self.__parent__.remove_client(self)
                    break
            else:
                if len(msg) > 0:
                    self.__parent__.process_client_requests(msg.decode('utf-8'), self)


from server.donkey_kong_server import Server
