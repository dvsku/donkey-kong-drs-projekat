import json
import multiprocessing as mp
import random
import threading
import time
import numpy as np
from threading import Thread, Lock
from common.constants import *
from common.enums.climb_state import ClimbState
from common.enums.collision_control_methods import CCMethods
from common.enums.direction import Direction
from common.enums.layout import Layouts
from common.enums.layout_block import LayoutBlock
from common.enums.player import Player
from common.enums.server_message import ServerMessage
from common.layout_builder import get_level_layout
from server.donkey_kong_server import Server
from server.models.collision.pipe_message import Message
from server.models.game_objects.barrel import Barrel
from server.models.game_objects.coin import Coin
from server.models.game_objects.gorilla import Gorilla
from server.models.game_objects.princess import Princess
from server.models.networking.client import Client


class Match:
    def __init__(self, parent: 'Server'):
        self.__parent__ = parent
        self.players = []
        self.princess = Princess()
        self.princess_reached = False
        self.gorilla = Gorilla()
        self.coin = Coin()
        self.current_scene = 1
        self.kill_thread = False
        self.kill_thread_lock = Lock()
        self.barrels_lock = Lock()
        self.ending = False
        self.cc_endpoint = self.__add_cc_endpoint()
        self.level_layout = None
        self.barrel_speed = 0.03
        self.barrels = np.array([Barrel(i) for i in range(BARREL_POOL_SIZE)])

        self.players_falling_thread = Thread(target=self.__players_falling_thread_do_work)
        self.barrels_fall_thread = Thread(target=self.__barrels_fall_thread_do_work)
        self.check_end_match_thread = Thread(target=self.__check_end_match_thread_do_work)
        self.princess_collision_thread = Thread(target=self.__princess_collision_thread_do_work)
        self.gorilla_thread = Thread(target=self.__gorilla_thread_do_work)
        self.gorilla_collision_thread = Thread(target=self.__gorilla_collision_thread_do_work)
        self.coin_thread = Thread(target=self.__coin_thread_do_work)


    """ Starts object threads """
    def start_threads(self):
        self.players_falling_thread.start()
        self.barrels_fall_thread.start()
        self.princess_collision_thread.start()
        self.gorilla_thread.start()
        self.gorilla_collision_thread.start()
        self.check_end_match_thread.start()
        self.coin_thread.start()

    """ Sets the scene layout, notifies players to load the scene """
    def load_scene(self):
        if self.current_scene == 1:
            self.set_level_layout(Layouts.FirstLevel)
        elif self.current_scene == 2:
            self.set_level_layout(Layouts.SecondLevel)
        elif self.current_scene == 3:
            self.set_level_layout(Layouts.ThirdLevel)
        elif self.current_scene == 4:
            self.set_level_layout(Layouts.FourthLevel)
        elif self.current_scene == 5:
            self.set_level_layout(Layouts.FifthLevel)

        self.barrel_speed /= BARREL_SPEED_MULTIPLIER
        message = json.dumps(
            { "command": ServerMessage.LOAD_GAME_SCENE.value, "layout": self.current_scene, "player": Player.PLAYER_1.value,
              "my_lives": self.players[0].lives, "opponent_lives": self.players[1].lives })
        self.players[0].send(message)
        message = json.dumps(
            { "command": ServerMessage.LOAD_GAME_SCENE.value, "layout": self.current_scene, "player": Player.PLAYER_2.value,
              "my_lives": self.players[1].lives, "opponent_lives": self.players[0].lives })
        self.players[1].send(message)
        self.__reset_barrels()
        self.princess_reached = False
        self.players[0].ready = False
        self.players[1].ready = False
        self.players[0].highest_y = 600
        self.players[1].highest_y = 600

    """ Sends a message to all players in the match """
    def send_to_all(self, msg):
        for player in self.players:
            player.send(msg)

    """ Sends a message to the opponent """
    def send_to_opponent(self, msg, player: Client):
        for p in self.players:
            if p != player:
                p.send(msg)

    """ Adds a player to the match """
    def add_player(self, player: Client):
        self.players.append(player)

    """ Removes the player from the match and ends the match if favor of his opponent """
    def player_disconnected(self, player: 'Client'):
        self.players.remove(player)
        self.__end()

    """ Checks if a player can move in the desired direction. """
    def move(self, player: Client, direction: Direction):
        player.latest_direction = direction
        if direction == Direction.LEFT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_L, player.x))
            msg = self.cc_endpoint.recv()
            self.__move_left(player, msg)
        elif direction == Direction.RIGHT:
            self.cc_endpoint.send(Message(CCMethods.END_OF_SCREEN_R, player.x))
            msg = self.cc_endpoint.recv()
            self.__move_right(player, msg)
        elif direction == Direction.UP:
            self.cc_endpoint.send(Message(CCMethods.CLIMB_UP, player.x, player.y, self.level_layout))
            msg = self.cc_endpoint.recv()
            self.__move_up(player, msg)
        elif direction == Direction.DOWN:
            self.cc_endpoint.send(Message(CCMethods.CLIMB_DOWN, player.x, player.y, self.level_layout))
            msg = self.cc_endpoint.recv()
            self.__move_down(player, msg)

    """ Sets the layout of the current level """
    def set_level_layout(self, layout: Layouts):
        self.level_layout = get_level_layout(layout.value)
        self.__set_starting_pos()

    """ Resets player lives """
    def reset_lives(self):
        for player in self.players:
            player.lives = PLAYER_LIVES

    """ Checks if a player should fall. Notifies both players to move the avatar of the falling player down. """
    def __players_falling_thread_do_work(self):
        thread_endpoint = self.__add_cc_endpoint()
        while not self.__check_thread_kill():
            if self.players[0].ready is True and self.players[1].ready is True:
                for player in self.players:
                    if player.x is not None and player.y is not None and (
                            player.latest_direction == Direction.LEFT or player.latest_direction == Direction.RIGHT):
                        thread_endpoint.send(Message(CCMethods.FALLING, player.x, player.y, player.latest_direction, self.level_layout))
                        msg = thread_endpoint.recv()
                        if msg.args[0]:
                            player.falling = True
                            message = json.dumps({ "command": ServerMessage.FALL.value })
                            player.send(message)
                            message = json.dumps({ "command": ServerMessage.FALL_OPPONENT.value })
                            self.send_to_opponent(message, player)
                            player.y += 5
                        else:
                            player.falling = False

            time.sleep(0.02)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    """ Checks if both players are dead """
    def __check_end_match_thread_do_work(self):
        while self.__check_thread_kill() is False and self.__check_end_match() is False:
            time.sleep(0.1)

        self.__end()

    """ Handles barrel movement, removing and collision with players """
    def __barrels_fall_thread_do_work(self):
        thread_endpoint = self.__add_cc_endpoint()
        while not self.__check_thread_kill():
            if not self.princess_reached and self.players[0].ready and self.players[1].ready:
                for index, barrel in enumerate(self.barrels):
                    if barrel.drawn:
                        thread_endpoint.send(Message(CCMethods.END_OF_SCREEN_V, barrel.y))
                        msg = thread_endpoint.recv()
                        # barrel reached end of screen, remove it
                        if msg.args[0]:
                            message = json.dumps({ "command": ServerMessage.REMOVE_BARREL.value, "index": index })
                            self.send_to_all(message)
                            barrel.drawn = False
                        # barrel has not reached end of screen, fall
                        else:
                            move_barrel = True
                            for player in self.players:
                                if barrel.x is not None and barrel.y is not None and player.x is not None and player.y is not None:
                                    thread_endpoint.send(Message(CCMethods.BARREL_COLLISION, barrel.x, barrel.y, player.x, player.y))
                                    msg = thread_endpoint.recv()
                                    if msg.args[0]:
                                        self.__reset_player_pos(player)
                                        player.lose_life()
                                        message = json.dumps({ "command": ServerMessage.HIT.value, "index": index, "lives": player.lives })
                                        player.send(message)
                                        message = json.dumps(
                                            { "command": ServerMessage.OPPONENT_HIT.value, "index": index, "lives": player.lives })
                                        self.send_to_opponent(message, player)

                                        barrel.drawn = False
                                        move_barrel = False

                                    if move_barrel:
                                        message = json.dumps({ "command": ServerMessage.MOVE_BARREL.value, "index": index })
                                        self.send_to_all(message)
                                        barrel.y += 5
            time.sleep(self.barrel_speed)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    """ Handles collision with princess, starts next level upon collision """
    def __princess_collision_thread_do_work(self):
        thread_endpoint = self.__add_cc_endpoint()
        while not self.__check_thread_kill():
            if self.princess_reached is False and self.players[0].ready is True and self.players[1].ready is True:
                for player in self.players:
                    if player.x is not None and player.y is not None:
                        thread_endpoint.send(Message(CCMethods.PRINCESS_COLLISION, self.princess.x, self.princess.y, player.x, player.y))
                        msg = thread_endpoint.recv()
                        if msg.args[0]:
                            self.princess_reached = True
                            self.__set_current_scene()
                            self.load_scene()

            time.sleep(0.03)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    """ Handles collision with gorilla """
    def __gorilla_collision_thread_do_work(self):
        thread_endpoint = self.__add_cc_endpoint()
        while not self.__check_thread_kill():
            if self.princess_reached is False and self.players[0].ready is True and self.players[1].ready is True:
                for player in self.players:
                    if player.x is not None and player.y is not None:
                        thread_endpoint.send(Message(CCMethods.GORILLA_COLLISION, self.gorilla.x, self.gorilla.y, player.x, player.y))
                        msg = thread_endpoint.recv()
                        if msg.args[0]:
                            self.__reset_player_pos(player)
                            player.lose_life()
                            message = json.dumps({ "command": ServerMessage.GORILLA_HIT.value, "lives": player.lives })
                            player.send(message)
                            message = json.dumps({ "command": ServerMessage.GORILLA_HIT_OPPONENT.value, "lives": player.lives })
                            self.send_to_opponent(message, player)
        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    """ Handles gorilla movement and barrel throwing """
    def __gorilla_thread_do_work(self):
        count = 0
        while not self.__check_thread_kill():
            if not self.princess_reached and self.players[0].ready is True and self.players[1].ready is True:
                if count == GORILLA_BARREL_THROW_DELAY:
                    self.__gorilla_throw_barrel()
                    count = 0
                    time.sleep(0.8)
                else:
                    self.__gorilla_move()
                    time.sleep(0.2)

                count += 1

    """ Handles coin drawing and removal """
    def __coin_thread_do_work(self):
        thread_endpoint = self.__add_cc_endpoint()
        while not self.__check_thread_kill():
            if self.princess_reached is False and self.players[0].ready is True and self.players[1].ready is True:
                if self.coin.drawn is False:
                    time.sleep(10)
                    self.__coin_set_position()
                    self.coin.drawn = True
                    message = json.dumps({ "command": ServerMessage.DRAW_COIN.value, "x": self.coin.x, "y": self.coin.y })
                    self.send_to_all(message)
                else:
                    for player in self.players:
                        if player.x is not None and player.y is not None:
                            thread_endpoint.send(Message(CCMethods.COIN_COLLISION, self.coin.x, self.coin.y, player.x, player.y))
                            msg = thread_endpoint.recv()

                            if msg.args[0]:
                                self.coin.drawn = False
                                message = json.dumps({ "command": ServerMessage.REMOVE_COIN.value })
                                self.send_to_all(message)
                                self.__coin_add_effect(player)

        thread_endpoint.send(Message(CCMethods.KILL_PROCESS))
        thread_endpoint.close()

    """ Sets coin position """
    def __coin_set_position(self):
        rows = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)
        columns = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)

        while True:
            row = np.random.randint(0, rows)
            column = np.random.randint(0, columns)

            if self.level_layout[row][column] == LayoutBlock.Platform:
                break

        self.coin.x = column * SCENE_GRID_BLOCK_WIDTH
        self.coin.y = (row - 1) * SCENE_GRID_BLOCK_HEIGHT

    """ Sends coin effect messages """
    def __coin_add_effect(self, player: Client):
        effect = np.random.randint(0, 2)
        if effect == 0:
            if player.lives == PLAYER_LIVES:
                return
            player.lives += 1
            message = json.dumps({ "command": ServerMessage.EFFECT_GAIN_LIFE.value, "lives": player.lives })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.EFFECT_GAIN_LIFE_OPPONENT.value, "lives": player.lives })
            self.send_to_opponent(message, player)
        elif effect == 1:
            player.lives -= 1
            message = json.dumps({ "command": ServerMessage.EFFECT_LOSE_LIFE.value, "lives": player.lives })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.EFFECT_LOSE_LIFE_OPPONENT.value, "lives": player.lives })
            self.send_to_opponent(message, player)

    """ Notifies both players to move the gorilla """
    def __gorilla_move(self):
        random_direction = random.choice([Direction.LEFT, Direction.RIGHT])
        x = int(self.gorilla.x / SCENE_GRID_BLOCK_WIDTH)
        if random_direction == Direction.LEFT:
            if not x <= self.gorilla.bound_start:
                move_direction = Direction.LEFT
            else:
                move_direction = Direction.RIGHT
        else:
            if not x >= self.gorilla.bound_end:
                move_direction = Direction.RIGHT
            else:
                move_direction = Direction.LEFT

        if move_direction == Direction.LEFT:
            self.gorilla.x -= 40
        elif move_direction == Direction.RIGHT:
            self.gorilla.x += 40

        message = json.dumps({ "command": ServerMessage.GORILLA_MOVE.value, "direction": move_direction.value })
        self.send_to_all(message)

    """ Notifies both players to draw a barrel """
    def __gorilla_throw_barrel(self):
        for barrel in self.barrels:
            if not barrel.drawn:
                barrel.drawn = True
                barrel.set_coordinates(self.gorilla.x + 14, self.gorilla.y + 40)
                message = json.dumps(
                    { "command": ServerMessage.GORILLA_THROW_BARREL.value, "x": barrel.x, "y": barrel.y, "index": barrel.index })
                self.send_to_all(message)
                break

    """ Thread safe check if threads should terminate """
    def __check_thread_kill(self):
        self.kill_thread_lock.acquire()
        ret_val = self.kill_thread
        self.kill_thread_lock.release()
        return ret_val

    """ Checks if both players are dead """
    def __check_end_match(self) -> bool:
        if self.players[0].lives <= 0 and self.players[1].lives <= 0:
            return True
        return False

    """ Notifies both players to move the player avatar left """
    def __move_left(self, player: Client, msg: Message):
        # player is not at the edge of the screen
        if not msg.args[0]:
            player.x -= 5
            message = json.dumps({ "command": ServerMessage.MOVE.value, "direction": Direction.LEFT.value })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.MOVE_OPPONENT.value, "direction": Direction.LEFT.value })
            self.send_to_opponent(message, player)
        # player is at the edge of the screen
        else:
            message = json.dumps({ "command": ServerMessage.STOP.value })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.STOP_OPPONENT.value })
            self.send_to_opponent(message, player)

    """ Notifies both players to move the player avatar right """
    def __move_right(self, player: Client, msg: Message):
        # player is not at the edge of the screen
        if not msg.args[0]:
            player.x += 5
            message = json.dumps({ "command": ServerMessage.MOVE.value, "direction": Direction.RIGHT.value })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.MOVE_OPPONENT.value, "direction": Direction.RIGHT.value })
            self.send_to_opponent(message, player)
        # player is at the edge of the screen
        else:
            message = json.dumps({ "command": ServerMessage.STOP.value })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.STOP_OPPONENT.value })
            self.send_to_opponent(message, player)

    """ Notifies both players to move the player avatar up """
    def __move_up(self, player: Client, msg: Message):
        if msg.args[0] == ClimbState.CLIMB or msg.args[0] == ClimbState.FINISH:
            player.y -= 5
            player.climbing = True

        if msg.args[0] == ClimbState.NONE and player.climbing is True:
            player.add_point()
            message = json.dumps({ "command": ServerMessage.SET_POINTS.value, "points": player.points })
            player.send(message)
            message = json.dumps({ "command": ServerMessage.SET_POINTS_OPPONENT.value, "points": player.points })
            self.send_to_opponent(message, player)
            player.climbing = False

        message = json.dumps({ "command": ServerMessage.CLIMB_UP.value, "climb_state": msg.args[0].value })
        player.send(message)
        message = json.dumps({ "command": ServerMessage.CLIMB_UP_OPPONENT.value, "climb_state": msg.args[0].value })
        self.send_to_opponent(message, player)

    """ Notifies both players to move the player avatar down """
    def __move_down(self, player: Client, msg: Message):
        if msg.args[0] == ClimbState.CLIMB or msg.args[0] == ClimbState.FINISH:
            player.y += 5

        message = json.dumps({ "command": ServerMessage.CLIMB_DOWN.value, "climb_state": msg.args[0].value })
        player.send(message)
        message = json.dumps({ "command": ServerMessage.CLIMB_DOWN_OPPONENT.value, "climb_state": msg.args[0].value })
        self.send_to_opponent(message, player)

    """ Stops running threads, closes all pipes to collision control and notifies players that the match ended """
    def __end(self):
        self.kill_thread_lock.acquire()
        self.kill_thread = True
        self.kill_thread_lock.release()
        self.ending = True
        message = json.dumps({ "command": ServerMessage.MATCH_ENDED.value })
        self.send_to_all(message)

        if self.barrels_fall_thread.isAlive() and threading.current_thread() != self.barrels_fall_thread:
            self.barrels_fall_thread.join()
        if self.players_falling_thread.isAlive() and threading.current_thread() != self.players_falling_thread:
            self.players_falling_thread.join()
        if self.princess_collision_thread.isAlive() and threading.current_thread() != self.princess_collision_thread:
            self.princess_collision_thread.join()
        if self.gorilla_thread.isAlive() and threading.current_thread() != self.gorilla_thread:
            self.gorilla_thread.join()
        if self.gorilla_collision_thread.isAlive() and threading.current_thread() != self.gorilla_collision_thread:
            self.gorilla_collision_thread.join()
        if self.check_end_match_thread.isAlive() and threading.current_thread() != self.check_end_match_thread:
            self.check_end_match_thread.join()
        if self.coin_thread.isAlive() and threading.current_thread() != self.coin_thread:
            self.coin_thread.join()

        self.cc_endpoint.send(Message(CCMethods.KILL_PROCESS))
        if self.__parent__.matches.__contains__(self):
            self.__parent__.matches.remove(self)

    """ Creates a pipe between collision control and this match """
    def __add_cc_endpoint(self) -> 'mp.Connection':
        parent, child = mp.Pipe()
        self.__parent__.cc_endpoint.send(Message(CCMethods.ADD_ENDPOINT, child))
        return parent

    """ Sets starting positions for players, princess, gorilla and gorilla movement boundaries """
    def __set_starting_pos(self):
        rows = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)
        columns = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)

        gorilla_x = 0
        gorilla_y = 0
        for row in range(rows):
            for column in range(columns):
                if self.level_layout[row][column] == LayoutBlock.Player_1:
                    self.players[0].starting_x = column * SCENE_GRID_BLOCK_WIDTH
                    self.players[0].starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                elif self.level_layout[row][column] == LayoutBlock.Player_2:
                    self.players[1].starting_x = column * SCENE_GRID_BLOCK_WIDTH + 13
                    self.players[1].starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                elif self.level_layout[row][column] == LayoutBlock.Princess:
                    self.princess.x = column * SCENE_GRID_BLOCK_WIDTH
                    self.princess.y = row * SCENE_GRID_BLOCK_HEIGHT
                elif self.level_layout[row][column] == LayoutBlock.Gorilla:
                    self.gorilla.x = column * SCENE_GRID_BLOCK_WIDTH
                    self.gorilla.y = row * SCENE_GRID_BLOCK_HEIGHT - 15
                    gorilla_x = column
                    gorilla_y = row

        for i in range(gorilla_x, 0, -1):
            if self.level_layout[gorilla_y + 1][i] is None:
                self.gorilla.bound_start = i + 1
                break

        for i in range(gorilla_x, columns):
            if self.level_layout[gorilla_y + 1][i] is None:
                self.gorilla.bound_end = i - 1
                break

    """ Sets the current layout of the scene """
    def __set_current_scene(self):
        if self.current_scene == 5:
            self.current_scene = 1
        else:
            self.current_scene += 1

    """ Resets player positions to their starting ones fot that scene """
    def __reset_player_pos(self, player: Client):
        player.x = player.starting_x
        player.y = player.starting_y

    """ Thread safe deleting of all barrels """
    def __reset_barrels(self):
        self.barrels_lock.acquire()
        for barrel in self.barrels:
            barrel.drawn = False
        self.barrels_lock.release()
