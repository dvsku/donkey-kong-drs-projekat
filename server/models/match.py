# region Imports
import multiprocessing as mp
import random
import time

import numpy as np

from client.globals import CCMethods, Direction, BARREL_POOL_SIZE, SCENE_WIDTH
from client.models.helper.pipe_message import Message
from common.layout_builder import get_level_layout
from server.models.game_objects.barrel import Barrel
from server.models.networking.client import Client
from common.enums import ServerMessage, MessageFormat, Layouts
from threading import Thread


# endregion

class Match:
    def __init__(self, parent):
        self.__parent__ = parent
        self.players = []
        self.kill_thread = False
        self.cc_endpoint = self.add_cc_endpoint()
        self.level_layout = None

        self.barrel_draw_y = 80
        self.barrels = np.array([Barrel(i) for i in range(BARREL_POOL_SIZE)])

        self.players_falling_thread = Thread(target=self.players_falling_thread_do_work)
        self.barrels_draw_thread = Thread(target=self.barrels_draw_thread_do_work)
        self.barrels_fall_thread = Thread(target=self.barrels_fall_thread_do_work)

    # region Thread workers

    """
    Checks if a player should fall. Notifies both players to move the avatar of the falling player
    down. Has it's own pipe for communication with collision control.
    """

    def players_falling_thread_do_work(self):
        thread_endpoint = self.add_cc_endpoint()
        while not self.kill_thread:
            for player in self.players:
                if player.x is not None and player.y is not None and player.latest_direction is not None:
                    thread_endpoint.send(Message(CCMethods.FALLING, player.x, player.y,
                                                 player.latest_direction, self.level_layout))
                    msg = thread_endpoint.recv()
                    if msg.args[0]:
                        player.falling = True
                        message = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.FALL.value)
                        player.send(message)
                        message = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.FALL_OPPONENT.value)
                        self.send_to_opponent(message, player)
                    else:
                        player.falling = False

            time.sleep(0.02)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    def barrels_draw_thread_do_work(self):
        while not self.kill_thread:
            time.sleep(5)
            for barrel in self.barrels:
                if not barrel.drawn:
                    barrel.drawn = True
                    barrel.y = self.barrel_draw_y
                    barrel.x = random.randrange(0, SCENE_WIDTH - 40)
                    msg = MessageFormat.COMMAND_DRAW_BARREL.value.format(ServerMessage.DRAW_BARREL.value,
                                                                         barrel.x, barrel.y, barrel.index)
                    self.send_to_all(msg)
                    break

    def barrels_fall_thread_do_work(self):
        thread_endpoint = self.add_cc_endpoint()
        while not self.kill_thread:
            for index, barrel in enumerate(self.barrels):
                if barrel.drawn:
                    thread_endpoint.send(Message(CCMethods.END_OF_SCREEN_V, barrel.y))
                    msg = thread_endpoint.recv()
                    # barrel reached end of screen, remove it
                    if msg.args[0]:
                        message = MessageFormat.COMMAND_REMOVE_BARREL.value.format(ServerMessage.REMOVE_BARREL.value,
                                                                                   index)
                        self.send_to_all(message)
                        barrel.drawn = False
                    # barrel has not reached end of screen, fall
                    else:
                        move_barrel = True
                        for player in self.players:
                            if barrel.x is not None and barrel.y is not None and player.x is not None \
                                    and player.y is not None:
                                thread_endpoint.send(Message(CCMethods.BARREL_COLLISION, barrel.x, barrel.y,
                                                             player.x, player.y))
                                msg = thread_endpoint.recv()
                                if msg.args[0]:
                                    message = MessageFormat.COMMAND_REMOVE_BARREL.value.format(
                                        ServerMessage.HIT.value, index
                                    )
                                    player.send(message)
                                    message = MessageFormat.COMMAND_REMOVE_BARREL.value.format(
                                        ServerMessage.OPPONENT_HIT.value, index
                                    )
                                    self.send_to_opponent(message, player)
                                    barrel.drawn = False
                                    move_barrel = False

                                if move_barrel:
                                    message = MessageFormat.COMMAND_MOVE_BARREL.value.format(
                                        ServerMessage.MOVE_BARREL.value,
                                        index
                                    )
                                    self.send_to_all(message)
                                    barrel.y += 5
            time.sleep(0.03)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    # endregion

    # region Player request processing

    """ 
    Checks if a player can move in the desired direction. If a player can move then notify both players to move
    the avatar of the player that sent the request, else notify both players to reset the avatar to default sprite.    
    """

    def move(self, player, x, y, direction):
        msg = None
        if direction == Direction.LEFT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_L, x))
            msg = self.cc_endpoint.recv()
        elif direction == Direction.RIGHT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_R, x))
            msg = self.cc_endpoint.recv()

        player.latest_direction = direction

        if msg is not None:
            if not msg.args[0]:
                message = MessageFormat.COMMAND_MOVE.value.format(ServerMessage.MOVE.value,
                                                                  direction.value,
                                                                  0, 0)
                player.send(message)
                message = MessageFormat.COMMAND_MOVE.value.format(ServerMessage.MOVE_OPPONENT.value,
                                                                  direction.value,
                                                                  0, 0)
                self.send_to_opponent(message, player)
            else:
                message = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.STOP.value)
                player.send(message)
                message = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.STOP_OPPONENT.value)
                self.send_to_opponent(message, player)

    # endregion

    # region Communication with players

    """ Sends a message to all players in the match """

    def send_to_all(self, msg):
        for player in self.players:
            player.send(msg)

    """ Sends a message to the opponent """

    def send_to_opponent(self, msg, player):
        for p in self.players:
            if p != player:
                p.send(msg)

    # endregion

    # region Match controls

    def start_threads(self):
        self.players_falling_thread.start()
        self.barrels_draw_thread.start()
        self.barrels_fall_thread.start()

    """ Stops running threads, closes all pipes to collision control and notifies players that the match ended """

    def end(self):
        self.kill_thread = True
        msg = MessageFormat.ONLY_COMMAND.value.format(ServerMessage.MATCH_ENDED.value)
        self.cc_endpoint.send(Message(CCMethods.KILL_PROCESS))
        self.send_to_all(msg)

    """ Removes the player from the match and ends the match if favor of his opponent """

    def player_disconnected(self, player: Client):
        self.players.remove(player)
        self.end()

    """ Adds a player to the match """

    def add_player(self, player: Client):
        self.players.append(player)

    """ Creates a pipe between collision control and this match """

    def add_cc_endpoint(self):
        parent, child = mp.Pipe()
        self.__parent__.cc_endpoint.send(Message(CCMethods.ADD_ENDPOINT, child))
        return parent

    """ Sets the layout of the current level """

    def set_level_layout(self, layout: Layouts):
        self.level_layout = get_level_layout(layout.value)

    # endregion
