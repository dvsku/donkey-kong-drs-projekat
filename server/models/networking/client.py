import socket
from threading import Thread


class Client:
    def __init__(self, parent, socket=None):
        self.__parent__ = parent
        self.kill_thread = False
        self.x = None
        self.y = None
        self.latest_direction = None
        self.falling = False
        self.socket = socket
        self.socket.settimeout(2)
        self.thread = Thread(target=self.do_work)
        self.thread.start()

    def set_coordinates(self, x, y):
        self.x = x
        self.y = y

    def do_work(self):
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

    def close(self):
        self.socket.close()
        self.kill_thread = True

    def send(self, msg):
        try:
            self.socket.send(bytes(msg, 'utf-8'))
        except OSError:
            pass
