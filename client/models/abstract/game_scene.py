from threading import Thread
import time
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem
from client.globals import *
from client.models.abstract.playable_character import PlayableCharacter
from client.models.game_objects.barrel import Barrel
from client.models.game_objects.first_player import FirstPlayer
from client.models.game_objects.ladder import Ladder
from client.models.game_objects.second_player import SecondPlayer
from common.enums import Player, MessageFormat, ClientMessage


class GameScene(QGraphicsScene):
    def __init__(self, parent, player: Player):
        super().__init__()
        self.__parent__ = parent
        self.grid = []
        self.grid_visible = True
        self.kill_thread = False

        self.me = None
        self.opponent = None

        if player == Player.PLAYER_1:
            self.me = FirstPlayer(self, 0, 0)
            self.opponent = SecondPlayer(self, 0, 0)
        else:
            self.me = SecondPlayer(self, 0, 0)
            self.opponent = FirstPlayer(self, 0, 0)

        self.move_thread = Thread(target=self.move_thread_do_work)
        self.pos_update_thread = Thread(target=self.pos_update_do_work)

        self.barrel_pool = np.array([Barrel(self, i) for i in range(BARREL_POOL_SIZE)])
        self.princess = None

    # region Barrels
    def draw_barrel(self, index):
        self.addItem(self.barrel_pool[index].item)

    def remove_barrel(self, index):
        self.removeItem(self.barrel_pool[index].item)
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

    # region Player Thread
    def move_self(self):
        direction = None
        if Qt.Key_W in self.me.keys_pressed:
            direction = Direction.UP
        elif Qt.Key_S in self.me.keys_pressed:
            direction = Direction.DOWN
        elif Qt.Key_A in self.me.keys_pressed:
            direction = Direction.LEFT
        elif Qt.Key_D in self.me.keys_pressed:
            direction = Direction.RIGHT

        # self.me.move_signal.emit(direction)
        self.me.latest_direction = direction
        msg = MessageFormat.COMMAND_MOVE.value.format(ClientMessage.MOVE.value, direction.value,
                                                      self.me.item.pos().x(),
                                                      self.me.item.pos().y())
        self.__parent__.socket.send_to_server(msg)

    def move_thread_do_work(self):
        while not self.kill_thread:
            if len(self.me.keys_pressed) != 0:
                self.move_self()
            else:
                if self.me.latest_direction is not None:
                    self.me.animation_reset_signal.emit(self.me.latest_direction)
                    msg = MessageFormat.ONLY_COMMAND.value.format(ClientMessage.STOP.value)
                    self.__parent__.socket.send_to_server(msg)
                    self.me.latest_direction = None

            time.sleep(0.02)

    def pos_update_do_work(self):
        while not self.kill_thread:
            msg = MessageFormat.COMMAND_POS.value.format(ClientMessage.POS.value, self.me.item.pos().x(),
                                                         self.me.item.pos().y())
            self.__parent__.socket.send_to_server(msg)
            time.sleep(0.01)

    def player_thread_move_player(self, player: PlayableCharacter):
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

    # endregion

    # region KeyPressEvents
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return

        if event.key() in {Qt.Key_A, Qt.Key_D, Qt.Key_W, Qt.Key_S} and not event.key() in self.me.keys_pressed:
            self.me.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.me.keys_pressed:
            self.me.keys_pressed.remove(event.key())

    # endregion
