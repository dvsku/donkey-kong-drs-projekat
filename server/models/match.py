# region Imports
import json
import multiprocessing as mp
import random
import time
from threading import Thread

import numpy as np

from common.constants import BARREL_POOL_SIZE, SCENE_WIDTH
from common.enums.climb_state import ClimbState
from common.enums.collision_control_methods import CCMethods
from common.enums.direction import Direction
from common.enums.layout import Layouts
from common.enums.server_message import ServerMessage
from common.layout_builder import get_level_layout
from server.models.collision.pipe_message import Message
from server.models.game_objects.barrel import Barrel
from server.models.networking.client import Client


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
                if player.x is not None and player.y is not None and (player.latest_direction == Direction.LEFT or
                                                                      player.latest_direction == Direction.RIGHT):
                    thread_endpoint.send(Message(CCMethods.FALLING, player.x, player.y,
                                                 player.latest_direction, self.level_layout))
                    msg = thread_endpoint.recv()
                    if msg.args[0]:
                        player.falling = True
                        message = json.dumps({"command": ServerMessage.FALL.value})
                        player.send(message)
                        message = json.dumps({"command": ServerMessage.FALL_OPPONENT.value})
                        self.send_to_opponent(message, player)
                        player.y += 5
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
                    message = json.dumps({"command": ServerMessage.DRAW_BARREL.value,
                                          "x": barrel.x, "y": barrel.y, "index": barrel.index})
                    self.send_to_all(message)
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
                        message = json.dumps({"command": ServerMessage.REMOVE_BARREL.value, "index": index})
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
                                    message = json.dumps({"command": ServerMessage.HIT.value, "index": index})
                                    player.send(message)
                                    message = json.dumps({"command": ServerMessage.OPPONENT_HIT.value, "index": index})
                                    self.send_to_opponent(message, player)
                                    barrel.drawn = False
                                    move_barrel = False

                                if move_barrel:
                                    message = json.dumps({"command": ServerMessage.MOVE_BARREL.value, "index": index})
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

    def move(self, player, direction):
        player.latest_direction = direction
        if direction == Direction.LEFT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_L, player.x))
            msg = self.cc_endpoint.recv()
            self.move_left(player, msg)
        elif direction == Direction.RIGHT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_R, player.x))
            msg = self.cc_endpoint.recv()
            self.move_right(player, msg)
        elif direction == Direction.UP:
            self.cc_endpoint.send(Message(CCMethods.CLIMB_UP, player.x, player.y, self.level_layout))
            msg = self.cc_endpoint.recv()
            self.move_up(player, msg)
        elif direction == Direction.DOWN:
            self.cc_endpoint.send(Message(CCMethods.CLIMB_DOWN, player.x, player.y, self.level_layout))
            msg = self.cc_endpoint.recv()
            self.move_down(player, msg)

    def move_left(self, player, msg: Message):
        # player is not at the edge of the screen
        if not msg.args[0]:
            player.x -= 5
            message = json.dumps({"command": ServerMessage.MOVE.value, "direction": Direction.LEFT.value})
            player.send(message)
            message = json.dumps({"command": ServerMessage.MOVE_OPPONENT.value, "direction": Direction.LEFT.value})
            self.send_to_opponent(message, player)
        # player is at the edge of the screen
        else:
            message = json.dumps({"command": ServerMessage.STOP.value})
            player.send(message)
            message = json.dumps({"command": ServerMessage.STOP_OPPONENT.value})
            self.send_to_opponent(message, player)

    def move_right(self, player, msg: Message):
        # player is not at the edge of the screen
        if not msg.args[0]:
            player.x += 5
            message = json.dumps({"command": ServerMessage.MOVE.value, "direction": Direction.RIGHT.value})
            player.send(message)
            message = json.dumps({"command": ServerMessage.MOVE_OPPONENT.value, "direction": Direction.RIGHT.value})
            self.send_to_opponent(message, player)
        # player is at the edge of the screen
        else:
            message = json.dumps({"command": ServerMessage.STOP.value})
            player.send(message)
            message = json.dumps({"command": ServerMessage.STOP_OPPONENT.value})
            self.send_to_opponent(message, player)

    def move_up(self, player, msg: Message):
        if msg.args[0] == ClimbState.CLIMB or msg.args[0] == ClimbState.FINISH:
            player.y -= 5

        message = json.dumps({"command": ServerMessage.CLIMB_UP.value, "climb_state": msg.args[0].value})
        player.send(message)
        message = json.dumps({"command": ServerMessage.CLIMB_UP_OPPONENT.value, "climb_state": msg.args[0].value})
        self.send_to_opponent(message, player)

    def move_down(self, player, msg: Message):
        if msg.args[0] == ClimbState.CLIMB or msg.args[0] == ClimbState.FINISH:
            player.y += 5

        message = json.dumps({"command": ServerMessage.CLIMB_DOWN.value, "climb_state": msg.args[0].value})
        player.send(message)
        message = json.dumps({"command": ServerMessage.CLIMB_DOWN_OPPONENT.value, "climb_state": msg.args[0].value})
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
        message = json.dumps({"command": ServerMessage.MATCH_ENDED.value})
        self.cc_endpoint.send(Message(CCMethods.KILL_PROCESS))
        self.send_to_all(message)

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
