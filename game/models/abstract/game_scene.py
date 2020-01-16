import multiprocessing as mp
import threading
import time
import numpy as np
import random
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem
from game.globals import *
from game.models.abstract.playable_character import PlayableCharacter
from game.models.game_objects.barrel import Barrel
from game.models.game_objects.first_player import FirstPlayer
from game.models.game_objects.gorilla import Gorilla
from game.models.game_objects.ladder import Ladder
from game.models.game_objects.platform import Platform
from game.models.game_objects.princess import Princess
from game.models.game_objects.second_player import SecondPlayer
from game.models.helper.queue_message import Message

class GameScene(QGraphicsScene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.grid = []
        self.grid_visible = True
        self.kill_thread = False

        self.player_1_position = []
        self.player_2_position = []

        self.barrel_thread = threading.Thread(target=self.barrel_thread_do_work)
        self.players_thread = threading.Thread(target=self.player_thread_do_work)
        self.players_falling_thread = threading.Thread(target=self.player_falling_thread_do_work)
        self.gorilla_thread = threading.Thread(target=self.gorilla_thread_do_work)

        self.barrel_pool = np.array([Barrel(self, i) for i in range(BARREL_POOL_SIZE)])
        self.gorilla = Gorilla(self, 0, 0)
        self.princess = Princess(self, 0, 0)
        self.players = np.array([FirstPlayer(self, 0, 0), SecondPlayer(self, 0, 0)])

        self.game_objects = np.full(300, None).reshape(int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH),
                                                       int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT))

    def player_lose_life(self, index):
        self.__parent__.lives[index].remove_life()
        if self.__parent__.lives[index].remaining == 0:
            self.players[index].alive = False

    def add_cc_endpoint(self):
        parent, child = mp.Pipe()
        self.__parent__.cc_endpoint.send(Message(CCMethods.ADD_ENDPOINT, child))
        return parent

    # region Barrels

    def draw_barrel(self, index):
        self.addItem(self.barrel_pool[index].item)

    def remove_barrel(self, index):
        self.removeItem(self.barrel_pool[index].item)

    def get_free_barrel(self):
        index = -1
        for i, barrel in enumerate(self.barrel_pool):
            if not barrel.is_drawn:
                index = i

        return index

    # endregion

    # region Grid
    def draw_grid(self):
        rows = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)
        columns = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)

        for x in range(0, rows):
            x_coordinate = x * SCENE_GRID_BLOCK_WIDTH
            # draw a line from x_coordinate, 0 to x, SCENE_HEIGHT
            self.grid.append(self.addLine(x_coordinate, 0, x_coordinate, SCENE_HEIGHT, QPen(QColor(255, 255, 255))))

        for y in range(0, columns):
            y_coordinate = y * SCENE_GRID_BLOCK_HEIGHT
            # draw a line from 0, y_coordinate to SCENE_WIDTH, y_coordinate
            self.grid.append(self.addLine(0, y_coordinate, SCENE_WIDTH, y_coordinate, QPen(QColor(255, 255, 255))))

        for n in range(0, columns):
            for m in range(0, rows):
                font = QFont()
                font.setPointSize(7)
                text = QGraphicsTextItem("({}, {})".format(m, n))
                text.setDefaultTextColor(Qt.white)
                text.setFont(font)
                text.setPos(m * SCENE_GRID_BLOCK_HEIGHT, n * SCENE_GRID_BLOCK_WIDTH)
                self.addItem(text)
                self.grid.append(text)

        self.grid = np.asarray(self.grid)

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        for line in self.grid:
            line.setVisible(self.grid_visible)

    # endregion

    # region Collision
    def check_barrel_end_of_screen(self, pipe_endpoint, barrel: Barrel):
        pipe_endpoint.send(Message(
            CCMethods.END_OF_SCREEN_V,
            barrel.item.pos().y(),
        ))
        msg = pipe_endpoint.recv()

        if msg.args[0]:
            barrel.remove_signal.emit()

    def check_barrel_collision(self, pipe_endpoint, barrel: Barrel, player: PlayableCharacter):
        pipe_endpoint.send(Message(
            CCMethods.BARREL_COLLISION,
            barrel.item.pos().x(),
            barrel.item.pos().y(),
            barrel.item.boundingRect().width(),
            barrel.item.boundingRect().height(),
            player.item.pos().x(),
            player.item.pos().y(),
            player.item.boundingRect().width(),
            player.item.boundingRect().height()
        ))
        msg = pipe_endpoint.recv()

        if msg.args[0]:
            barrel.remove_signal.emit()
            player.lose_life_signal.emit()

    def check_princess_collision(self, pipe_endpoint, princess: Princess, player: PlayableCharacter):
        pipe_endpoint.send(Message(
            CCMethods.PRINCESS_COLLISION,
            princess.item.pos().x(),
            princess.item.pos().y(),
            princess.item.boundingRect().width(),
            princess.item.boundingRect().height(),
            player.item.pos().x(),
            player.item.pos().y(),
            player.item.boundingRect().width(),
            player.item.boundingRect().height()
        ))

        msg = pipe_endpoint.recv()
        return msg.args[0]

    def check_gorilla_collision(self, pipe_endpoint, gorilla: Gorilla, player: PlayableCharacter):
        pipe_endpoint.send(Message(
            CCMethods.GORILLA_COLLISION,
            gorilla.item.pos().x(),
            gorilla.item.pos().y(),
            gorilla.item.boundingRect().width(),
            gorilla.item.boundingRect().height(),
            player.item.pos().x(),
            player.item.pos().y(),
            player.item.boundingRect().width(),
            player.item.boundingRect().height()
        ))
        msg = pipe_endpoint.recv()
        if msg.args[0]:
            player.lose_life_signal.emit()

    def check_end_of_screen_left(self, pipe_endpoint, x):
        pipe_endpoint.send(Message(
            CCMethods.END_OF_SCREEN_L,
            x,
        ))
        msg = pipe_endpoint.recv()

        return msg.args[0]

    def check_end_of_screen_right(self, pipe_endpoint, x):
        pipe_endpoint.send(Message(
            CCMethods.END_OF_SCREEN_R,
            x,
        ))
        msg = pipe_endpoint.recv()

        return msg.args[0]

    def check_falling(self, player_x, player_y, direction: Direction):
        ret_value = False

        y = int(player_y / SCENE_GRID_BLOCK_HEIGHT)
        if direction == Direction.LEFT:
            x = int((player_x + 20) / SCENE_GRID_BLOCK_WIDTH)
        elif direction == Direction.RIGHT:
            x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
        else:
            return False

        if self.game_objects[x][y] is None:
            ret_value = True
        elif isinstance(self.game_objects[x][y], Platform):
            if self.game_objects[x][y].pos().y() != player_y:
                ret_value = True

        return ret_value

    def check_climbing(self, player_x, player_y, direction: Direction):
        # default return value, if it's NONE, don't climb
        ret_value = ClimbState.NONE

        # get x center point
        player_x_center = player_x + 13

        if direction == Direction.UP:
            # get x  of the block the player is in
            x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
            # get y of the block the player is in (feet level)
            y = int((player_y + 34) / SCENE_GRID_BLOCK_HEIGHT)

            if isinstance(self.game_objects[x][y], Ladder):
                # get climbable ladder x coordinates (the whole ladder is not climbable)
                ladder_x_from = self.game_objects[x][y].pos().x() + 5
                ladder_x_to = self.game_objects[x][y].pos().x() + 30

                # check if the player is between climbable x coordinates
                if (ladder_x_from < player_x_center) and (ladder_x_to > player_x_center):
                    # get y of the block at player head level
                    y = int((player_y + 3) / SCENE_GRID_BLOCK_HEIGHT)

                    # check if block above the player's head is empty
                    if self.game_objects[x][y] is None:
                        ret_value = ClimbState.FINISH
                    else:
                        ret_value = ClimbState.CLIMB
        elif direction == Direction.DOWN:
            # get x  of the block the player is in
            x = int(player_x / SCENE_GRID_BLOCK_WIDTH)
            # get y of the block the player is in (feet level)
            y = int((player_y + 35) / SCENE_GRID_BLOCK_HEIGHT)

            if isinstance(self.game_objects[x][y], Ladder):
                # get climbable ladder x coordinates (the whole ladder is not climbable)
                ladder_x_from = self.game_objects[x][y].pos().x() + 5
                ladder_x_to = self.game_objects[x][y].pos().x() + 30

                # check if the player is between climbable x coordinates
                if (ladder_x_from < player_x_center) and (ladder_x_to > player_x_center):
                    # get y of the block at player head level
                    y = int((player_y + 3) / SCENE_GRID_BLOCK_HEIGHT)

                    # check if block above the player's head is empty
                    if self.game_objects[x][y] is None:
                        ret_value = ClimbState.START
                    else:
                        ret_value = ClimbState.CLIMB

        return ret_value

    # endregion

    # region Barrel Thread
    def barrel_thread_do_work(self):
        thread_endpoint = self.add_cc_endpoint()
        while not self.kill_thread:
            for i in range(len(self.barrel_pool)):
                if self.barrel_pool[i].is_drawn:
                    self.barrel_pool[i].fall_signal.emit()
                    self.check_barrel_end_of_screen(thread_endpoint, self.barrel_pool[i])
                    if self.players[0].alive:
                        self.check_barrel_collision(thread_endpoint, self.barrel_pool[i], self.players[0])
                    if self.players[1].alive:
                        self.check_barrel_collision(thread_endpoint, self.barrel_pool[i], self.players[1])

            time.sleep(0.025)

        thread_endpoint.close()

    # endregion

    # region Player Thread
    def player_thread_do_work(self):
        thread_endpoint = self.add_cc_endpoint()
        while not self.kill_thread:
            self.check_end_game()
            for i, player in enumerate(self.players):
                if player.alive:
                    self.check_gorilla_collision(thread_endpoint, self.gorilla, player)
                    if self.check_princess_collision(thread_endpoint, self.princess, player):
                        self.__parent__.load_next_level()
                    if not player.falling:
                        if len(player.keys_pressed) != 0:
                            self.player_thread_move_player(thread_endpoint, player)
                        else:
                            self.player_thread_reset_animation(player)

            time.sleep(0.03)

        thread_endpoint.close()

    def check_end_game(self):
        if self.players[0].alive is False and self.players[1].alive is False:
            self.kill_thread = True
            self.__parent__.end_game_signal.emit()

    def player_thread_move_player(self, pipe_endpoint, player: PlayableCharacter):
        x = player.item.pos().x()
        y = player.item.pos().y()

        # up key
        if player.action_keys[0] in player.keys_pressed:
            player.latest_key = player.action_keys[0]
            result = self.check_climbing(x, y, Direction.UP)

            if result == ClimbState.CLIMB:
                player.climbing = True
                player.move_signal.emit(Direction.UP)
            elif result == ClimbState.FINISH:
                player.climbing = True
                player.climb_finish_signal.emit()
            elif result == ClimbState.NONE:
                player.climbing = False
                player.animation_reset_signal.emit(Direction.UP)
        # down key
        elif player.action_keys[1] in player.keys_pressed:
            player.latest_key = player.action_keys[1]
            result = self.check_climbing(x, y, Direction.DOWN)

            if result == ClimbState.CLIMB:
                player.climbing = True
                player.move_signal.emit(Direction.DOWN)
            elif result == ClimbState.START:
                player.climbing = True
                player.climb_start_signal.emit()
            elif result == ClimbState.NONE:
                player.climbing = False
                player.animation_reset_signal.emit(Direction.DOWN)
        # left key
        elif player.action_keys[2] in player.keys_pressed:
            if not player.climbing:
                if self.check_end_of_screen_left(pipe_endpoint, x):
                    player.animation_reset_signal.emit(Direction.LEFT)
                else:
                    player.move_signal.emit(Direction.LEFT)
                    player.latest_key = player.action_keys[2]
        # right key
        elif player.action_keys[3] in player.keys_pressed:
            if not player.climbing:
                if self.check_end_of_screen_right(pipe_endpoint, x):
                    player.animation_reset_signal.emit(Direction.RIGHT)
                else:
                    player.move_signal.emit(Direction.RIGHT)
                    player.latest_key = player.action_keys[3]

    def player_thread_reset_animation(self, player: PlayableCharacter):
        if player.latest_key == player.action_keys[2]:
            player.animation_reset_signal.emit(Direction.LEFT)
        elif player.latest_key == player.action_keys[3]:
            player.animation_reset_signal.emit(Direction.RIGHT)

    def player_falling_thread_do_work(self):
        thread_endpoint = self.add_cc_endpoint()
        while not self.kill_thread:
            for i in range(len(self.players)):
                player_x = self.players[i].item.pos().x()
                player_y = self.players[i].item.pos().y() + 35

                should_fall = False
                # left key
                if self.players[i].latest_key == self.players[i].action_keys[2]:
                    should_fall = self.check_falling(player_x, player_y, Direction.LEFT)
                # right key
                elif self.players[i].latest_key == self.players[i].action_keys[3]:
                    should_fall = self.check_falling(player_x, player_y, Direction.RIGHT)

                if should_fall:
                    self.players[i].falling = True
                    self.players[i].fall_signal.emit()
                else:
                    self.players[i].falling = False

            time.sleep(0.015)

        thread_endpoint.close()

    # endregion

    # region Gorilla Thread

    def gorilla_thread_do_work(self):
        count = 0
        while not self.kill_thread:
            count += 1
            if count % 5 == 0:
                self.gorilla_throwing_barrel()
                count = 0
                continue

            self.gorilla_thread_move_gorilla()
            time.sleep(0.2)

    def gorilla_thread_reset_animation(self):
        if self.gorilla.latest_direction == self.gorilla.randDirection[0]:
            self.gorilla.animation_reset_signal.emit(Direction.LEFT)
        elif self.gorilla.latest_direction == self.gorilla.randDirection[1]:
            self.gorilla.animation_reset_signal.emit(Direction.RIGHT)

    def gorilla_thread_move_gorilla(self):
        current_direction = random.choice(self.gorilla.randDirection)
        x = int(self.gorilla.item.x() / SCENE_GRID_BLOCK_WIDTH)
        if current_direction == Direction.LEFT:
            if not x <= 0:
                self.gorilla.move_signal.emit(Direction.LEFT)
            else:
                self.gorilla.move_signal.emit(Direction.RIGHT)
        else:
            if not x >= 15:
                self.gorilla.move_signal.emit(Direction.RIGHT)
            else:
                self.gorilla.move_signal.emit(Direction.LEFT)

    def gorilla_throwing_barrel(self):
        self.gorilla.throw_start_signal.emit()
        index = self.get_free_barrel()
        if index != -1:
            self.barrel_pool[index].item.setPos(self.gorilla.item.x() + 14, self.gorilla.item.y() + 40)
            self.barrel_pool[index].draw_signal.emit()
        time.sleep(0.8)
        self.gorilla_thread_reset_animation()
    # endregion

    # region KeyPressEvents
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif event.key() == Qt.Key_Escape:
            self.__parent__.load_main_menu()
            return

        if event.key() in {Qt.Key_A, Qt.Key_D, Qt.Key_W,
                           Qt.Key_S} and not event.key() in self.players[0].keys_pressed:
            self.players[0].keys_pressed.add(event.key())

        if event.key() in {Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down} and \
                not event.key() in self.players[1].keys_pressed:
            self.players[1].keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.players[0].keys_pressed:
            self.players[0].keys_pressed.remove(event.key())

        if event.key() in self.players[1].keys_pressed:
            self.players[1].keys_pressed.remove(event.key())

    # endregion
