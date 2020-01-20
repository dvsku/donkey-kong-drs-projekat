import atexit
import json
import multiprocessing as mp
import os
import sys
import time
import re
from json import JSONDecodeError
sys.path += [os.path.abspath('..')]
from common.enums.client_message import ClientMessage
from common.enums.direction import Direction
from common.enums.info_scenes import InfoScenes
from common.enums.server_message import ServerMessage
from server.models.collision.collision_control import CollisionControl
from server.models.networking.client import Client
from server.models.networking.server_socket import ServerSocket

class Server:
    def __init__(self, args):
        if len(args) != 3:
            print("Usage: python donkey_kong.py ip_address port")
            sys.exit()

        ip_address = args[1]
        try:
            port = int(args[2])
        except ValueError:
            print("Error: port has to be a number")
            sys.exit()

        atexit.register(self.__cleanup)
        self.kill_thread = False
        self.clients = []
        self.matches = []

        self.cc_endpoint = None
        self.__setup_collision_control()

        self.server_socket = ServerSocket(self, ip_address, port)

    """ Creates a client instance when connection has been established """
    def process_connection_established(self, msg, socket):
        message = json.loads(msg)
        if message['command'] == ClientMessage.CONNECTION_ESTABLISHED.value:
            client = Client(self, client_socket=socket)
            self.clients.append(client)
            message = json.dumps({"command": ServerMessage.CONNECTION_ACK.value})
            client.send(message)

    """ Used to process client requests and send responses """
    def process_client_requests(self, msg: str, client: Client):
        # split messages if they were received together
        messages = re.findall(r'({(.*?)})', msg)
        for message in messages:
            try:
                message = json.loads(message[0])
            except JSONDecodeError:
                return

            # player has requested a match
            if message['command'] == ClientMessage.REQUEST_GAME.value:
                self.__process_match_request(client)
            # player has disconnected or closed the game
            elif message['command'] == ClientMessage.CLOSE.value:
                self.__process_close_request(client)
            # player has moved
            elif message['command'] == ClientMessage.MOVE.value:
                self.__process_move_request(client, Direction(message['direction']))
            # player has stopped moving
            elif message['command'] == ClientMessage.STOP.value:
                self.__process_stop_request(client)
            # player has sent his positional data
            elif message['command'] == ClientMessage.POS.value:
                client.set_coordinates(message['x'], message['y'])
            # player has sent his ready check
            elif message['command'] == ClientMessage.READY.value:
                client.ready = True

    """ Removes the client """
    def remove_client(self, client: Client):
        if self.clients.__contains__(client):
            self.clients.remove(client)

    """ Stop client's match due to disconnect and declare his opponent the winner """
    def stop_match(self, player: Client):
        for match in self.matches:
            if match.players.__contains__(player):
                match.player_disconnected(player)
                if self.matches.__contains__(match):
                    self.matches.remove(match)
                break

    """ Starts up collision control process and adds the main pipe to it """
    def __setup_collision_control(self):
        parent, child = mp.Pipe()
        CollisionControl(child)
        self.cc_endpoint = parent

    """ Handles requests for a game """
    def __process_match_request(self, client: Client):
        # check if there is already a match with a player waiting for an opponent
        match = self.__get_waiting_match()
        # create a new match and notify the player that he's gonna wait for an opponent
        if match is None:
            match = Match(self)
            match.add_player(client)
            self.matches.append(match)
            message = json.dumps({ "command": ServerMessage.LOAD_INFO_SCENE.value, "scene": InfoScenes.WAITING_FOR_PLAYERS.value })
            match.send_to_all(message)
        # add the player to the match and notify both players to start the game on the first level
        else:
            match.add_player(client)
            match.reset_lives()
            match.load_scene()
            match.start_threads()

    """ Handles requests for removing the client """
    def __process_close_request(self, client: Client):
        # stop the match, and declare his opponent the winner
        self.stop_match(client)
        # close the player socket and remove him from clients list
        client.socket.close()
        self.remove_client(client)

    """ Handles player movement """
    def __process_move_request(self, client: Client, direction: Direction):
        # get players' match and notify both players to move the requesting players' avatar
        if not client.falling and client.x is not None and client.y is not None:
            match = self.__get_client_match(client)
            match.move(client, direction)
            time.sleep(0.02)

    """ Handles animation resets """
    def __process_stop_request(self, client: Client):
        # get players' match and notify both players to reset the requesting players' avatar to default sprite
        if client.x is not None and client.y is not None:
            match = self.__get_client_match(client)
            message = json.dumps({ "command": ServerMessage.STOP_OPPONENT.value })
            match.send_to_opponent(message, client)

    """ Gets a match that is waiting for a second player """
    def __get_waiting_match(self) -> 'Match':
        for match in self.matches:
            if len(match.players) < 2 and match.ending is False:
                return match
        return None

    """ Get client's match """
    def __get_client_match(self, player: Client) -> 'Match':
        for match in self.matches:
            if match.players.__contains__(player):
                return match
        return None

    """ Stops running threads """
    def __cleanup(self):
        self.kill_thread = True


from server.models.match import Match

if __name__ == '__main__':
    Server(sys.argv)
