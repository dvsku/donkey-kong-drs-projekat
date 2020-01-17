import json
import socket
from threading import Thread

from common.enums.client_message import ClientMessage


class ClientSocket:
    def __init__(self, parent):
        self.__parent__ = parent
        self.socket = None
        self.kill_thread = False
        self.thread = Thread(target=self.do_work)
        self.establish_connection()
        self.thread.start()

    def establish_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostname(), 1234))
        self.socket.settimeout(2)
        message = json.dumps({"command": ClientMessage.CONNECTION_ESTABLISHED.value})
        self.send_to_server(message)

    def send_to_server(self, msg):
        try:
            self.socket.send(bytes(msg, 'utf-8'))
        except ConnectionResetError:
            self.send_to_server(msg)

    def close(self):
        self.socket.close()
        self.kill_thread = True

    def do_work(self):
        while True:
            try:
                if self.kill_thread:
                    break
                msg = self.socket.recv(1024)
            except socket.error as e:
                if e.args[0] != "timed out":
                    break
            else:
                if len(msg) > 0:
                    self.__parent__.process_socket_message(msg.decode('utf-8'))
