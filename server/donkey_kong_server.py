import atexit
import json
import os
import sys
from json import JSONDecodeError

from common.enums.client_message import ClientMessage
from common.enums.direction import Direction
from common.enums.layout import Layouts
from common.enums.player import Player
from common.enums.scene import Scene
from common.enums.server_message import ServerMessage

sys.path += [os.path.abspath('..')]
from server.models.match import Match
from server.models.networking.client import Client
from server.models.networking.server_socket import ServerSocket
from server.models.collision.collision_control import CollisionControl
import multiprocessing as mp


class Server:
    # region Setup
    def __init__(self):
        atexit.register(self.cleanup)
        self.kill_thread = False
        self.clients = []
        self.matches = []

        self.cc_endpoint = None
        self.setup_collision_control()

        self.server_socket = ServerSocket(self)

    """ Starts up collision control process and adds the main pipe to it """

    def setup_collision_control(self):
        parent, child = mp.Pipe()
        CollisionControl(child)
        self.cc_endpoint = parent

    # endregion

    # region Client request processing

    """ Creates a client instance when connection has been established """

    def process_connection_established(self, msg, socket):
        message = json.loads(msg)
        if message['command'] == ClientMessage.CONNECTION_ESTABLISHED.value:
            client = Client(self, socket=socket)
            self.clients.append(client)
            message = json.dumps({"command": ServerMessage.CONNECTION_ACK.value})
            client.send(message)

    """ Used to process client requests and send responses """

    def process_client_requests(self, msg: str, client: Client):
        try:
            message = json.loads(msg)
        except JSONDecodeError:
            return

        # player has requested a match
        if message['command'] == ClientMessage.REQUEST_GAME.value:
            self.process_match_request(client)

        # player has disconnected or closed the game
        elif message['command'] == ClientMessage.CLOSE.value:
            self.process_close_request(client)

        # player has moved
        elif message['command'] == ClientMessage.MOVE.value:
            self.process_move_request(client, Direction(message['direction']))

        # player has stopped moving
        elif message['command'] == ClientMessage.STOP.value:
            self.process_stop_request(client)

        # player has sent his positional data
        elif message['command'] == ClientMessage.POS.value:
            client.set_coordinates(message['x'], message['y'])

    def process_match_request(self, client):
        # check if there is already a match with a player waiting for an opponent
        match = self.get_waiting_match()

        # create a new match and notify the player that he's gonna wait for an opponent
        if match is None:
            match = Match(self)
            match.add_player(client)
            self.matches.append(match)
            message = json.dumps({"command": ServerMessage.LOAD_SCENE.value,
                                  "scene": Scene.WAITING_FOR_PLAYERS.value, "player": Player.PLAYER_1.value})
            match.send_to_all(message)
        # add the player to the match and notify both players to start the game on the first level
        else:
            match.add_player(client)
            match.set_level_layout(Layouts.FirstLevel)
            message = json.dumps({"command": ServerMessage.LOAD_SCENE.value,
                                  "scene": Scene.FIRST_LEVEL.value, "player": Player.PLAYER_1.value})
            match.players[0].send(message)
            message = json.dumps({"command": ServerMessage.LOAD_SCENE.value,
                                  "scene": Scene.FIRST_LEVEL.value, "player": Player.PLAYER_2.value})
            match.players[1].send(message)
            match.start_threads()

    def process_close_request(self, client):
        # stop the match, and declare his opponent the winner
        self.stop_match(client)
        # close the player socket and remove him from clients list
        client.socket.close()
        self.remove_client(client)

    def process_move_request(self, client, direction):
        # get players' match and notify both players to move the requesting players' avatar
        if not client.falling:
            match = self.get_client_match(client)
            match.move(client, direction)

    def process_stop_request(self, client):
        # get players' match and notify both players to reset the requesting players' avatar to default sprite
        match = self.get_client_match(client)
        message = json.dumps({"command": ServerMessage.STOP_OPPONENT.value})
        match.send_to_opponent(message, client)

    # endregion

    # region Helpers
    def get_waiting_match(self):
        for match in self.matches:
            if len(match.players) < 2:
                return match
        return None

    def get_client_match(self, player):
        for match in self.matches:
            if match.players.__contains__(player):
                return match
        return None

    def stop_match(self, player):
        for match in self.matches:
            if match.players.__contains__(player):
                match.player_disconnected(player)
                self.matches.remove(match)
                break

    def remove_client(self, client):
        if self.clients.__contains__(client):
            self.clients.remove(client)

    def cleanup(self):
        self.kill_thread = True

    # endregion


if __name__ == '__main__':
    Server()
