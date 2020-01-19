from socket import *
from threading import Thread


class ServerSocket:
    def __init__(self, parent):
        self.__parent__ = parent
        self.socket = None
        self.thread = Thread(target=self.__do_work)
        self.__setup_socket()
        self.thread.start()

    def __setup_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        self.socket.bind((gethostname(), 1234))
        self.socket.listen(5)

    def __do_work(self):
        while True:
            client_socket, address = self.socket.accept()
            msg = client_socket.recv(1024)
            if len(msg) > 0:
                self.__parent__.process_connection_established(msg.decode('utf-8'), client_socket)
