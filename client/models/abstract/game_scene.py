import json
import time
from threading import Thread

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem

from client.models.game_objects.barrel import Barrel
from client.models.game_objects.first_player import FirstPlayer
from client.models.game_objects.second_player import SecondPlayer
from common.constants import BARREL_POOL_SIZE, SCENE_GRID_BLOCK_WIDTH, SCENE_GRID_BLOCK_HEIGHT, SCENE_WIDTH, \
    SCENE_HEIGHT
from common.enums.client_message import ClientMessage
from common.enums.direction import Direction
from common.enums.player import Player


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
            self.me = FirstPlayer(self)
            self.opponent = SecondPlayer(self)
        else:
            self.me = SecondPlayer(self)
            self.opponent = FirstPlayer(self)

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

        if (direction == Direction.LEFT or direction == Direction.RIGHT) and self.me.climbing:
            return

        self.me.latest_direction = direction
        message = json.dumps({"command": ClientMessage.MOVE.value, "direction": direction.value})
        self.__parent__.socket.send_to_server(message)

    def move_thread_do_work(self):
        while not self.kill_thread:
            if len(self.me.keys_pressed) != 0:
                self.move_self()
            else:
                if self.me.latest_direction is not None:
                    self.me.animation_reset_signal.emit(self.me.latest_direction)
                    message = json.dumps({"command": ClientMessage.STOP.value})
                    self.__parent__.socket.send_to_server(message)
                    self.me.latest_direction = None

            time.sleep(0.02)

    def pos_update_do_work(self):
        while not self.kill_thread:
            message = json.dumps({"command": ClientMessage.POS.value, "x": self.me.item.x(), "y": self.me.item.y()})
            self.__parent__.socket.send_to_server(message)
            time.sleep(0.1)

    def send_pos_update(self):
        message = json.dumps({"command": ClientMessage.POS.value, "x": self.me.item.x(), "y": self.me.item.y()})
        self.__parent__.socket.send_to_server(message)

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
