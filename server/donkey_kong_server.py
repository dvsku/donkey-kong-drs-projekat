import os
import sys
import atexit
import json
from json import JSONDecodeError
from client.globals import Direction

sys.path += [os.path.abspath('..')]
from server.models.match import Match
from server.models.networking.client import Client
from server.models.networking.server_socket import ServerSocket
from common.enums import ClientMessage, ServerMessage, Scene, MessageFormat, Player, Layouts
from server.collision_control import CollisionControl
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
            msg = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.CONNECTION_ACK.value)
            client.send(msg)

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
            self.process_move_request(client, message['x'], message['y'], Direction(message['direction']))

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
            msg = MessageFormat.COMMAND_SCENE.value.format(
                ServerMessage.LOAD_SCENE.value,
                Scene.WAITING_FOR_PLAYERS.value,
                Player.PLAYER_1.value
            )
            match.send_to_all(msg)
        # add the player to the match and notify both players to start the game on the first level
        else:
            match.add_player(client)
            match.set_level_layout(Layouts.FirstLevel)
            msg = MessageFormat.COMMAND_SCENE.value.format(
                ServerMessage.LOAD_SCENE.value,
                Scene.FIRST_LEVEL.value,
                Player.PLAYER_1.value
            )
            match.players[0].send(msg)
            msg = MessageFormat.COMMAND_SCENE.value.format(
                ServerMessage.LOAD_SCENE.value,
                Scene.FIRST_LEVEL.value,
                Player.PLAYER_2.value
            )
            match.players[1].send(msg)
            match.start_threads()

    def process_close_request(self, client):
        # stop the match, and declare his opponent the winner
        self.stop_match(client)
        # close the player socket and remove him from clients list
        client.socket.close()
        self.remove_client(client)

    def process_move_request(self, client, x, y, direction):
        # get players' match and notify both players to move the requesting players' avatar
        if not client.falling:
            match = self.get_client_match(client)
            match.move(client, x, y, direction)

    def process_stop_request(self, client):
        # get players' match and notify both players to reset the requesting players' avatar to default sprite
        match = self.get_client_match(client)
        msg = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.STOP_OPPONENT.value)
        match.send_to_opponent(msg, client)

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
