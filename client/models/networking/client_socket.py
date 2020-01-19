import json
from socket import *
from threading import Thread

from common.enums.client_message import ClientMessage


class ClientSocket:
    def __init__(self, parent):
        self.__parent__ = parent
        self.socket = None
        self.connection_established = False
        self.kill_thread = False
        self.thread = Thread(target=self.do_work)
        self.establish_connection()
        self.thread.start()

    def establish_connection(self):
        if not self.connection_established:
            self.socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
            self.socket.connect((gethostname(), 1234))
            self.socket.settimeout(2)
            message = json.dumps({ "command": ClientMessage.CONNECTION_ESTABLISHED.value })
            self.send_to_server(message)

    def send_to_server(self, msg):
        try:
            self.socket.send(bytes(msg, 'utf-8'))
        except ConnectionResetError:
            pass

    def close(self):
        self.socket.close()
        self.kill_thread = True

    def do_work(self):
        while True:
            try:
                if self.kill_thread:
                    break
                msg = self.socket.recv(1024)
            except error as e:
                if e.args[0] != "timed out":
                    break
            else:
                if len(msg) > 0:
                    self.__parent__.process_socket_message(msg.decode('utf-8'))
