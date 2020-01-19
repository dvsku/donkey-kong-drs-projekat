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
from client.models.helper.grid_painter import GridPainter
from common.constants import *
from common.enums.client_message import ClientMessage
from common.enums.direction import Direction
from common.enums.layout import Layouts
from common.enums.player import Player
from common.layout_builder import get_level_layout


class GameScene(QGraphicsScene):
    def __init__(self, parent, me: Player):
        super().__init__()
        self.__parent__ = parent
        self.grid = []
        self.grid_visible = True
        self.kill_thread = False
        self.princess = None
        self.gorilla = None
        self.barrel_pool = np.array([Barrel(self, i) for i in range(BARREL_POOL_SIZE)])
        self.me = None
        self.opponent = None
        self.set_players(me)
        self.move_thread = Thread(target=self.move_thread_do_work)
        self.move_thread.start()

    def load_layout_and_start(self, layout: Layouts):
        self.clear_scene()
        grid_painter = GridPainter()
        grid_painter.paint_layout(self, get_level_layout(layout))
        self.send_pos_update()

    def set_lives(self, mine: int, opponent: int):
        self.me.set_lives(mine)
        self.opponent.set_lives(opponent)

    def set_players(self, me: Player):
        if me == Player.PLAYER_1:
            self.me = FirstPlayer(self)
            self.opponent = SecondPlayer(self)
        else:
            self.me = SecondPlayer(self)
            self.opponent = FirstPlayer(self)

    def draw_lives(self):
        if isinstance(self.me, FirstPlayer):
            self.me.lives.setPos(0, 0)
            self.opponent.lives.setPos(SCENE_WIDTH - self.opponent.lives.boundingRect().width(), 0)
        else:
            self.me.lives.setPos(SCENE_WIDTH - self.opponent.lives.boundingRect().width(), 0)
            self.opponent.lives.setPos(0, 0)
        self.addItem(self.me.lives)
        self.addItem(self.opponent.lives)

    def draw_points(self):
        self.set_points_position()
        self.addItem(self.me.points)
        self.addItem(self.opponent.points)

    def set_points_position(self):
        if isinstance(self.me, FirstPlayer):
            self.me.points.setPos(130, -5)
            self.opponent.points.setPos(SCENE_WIDTH - (130 + self.opponent.points.boundingRect().width()), -5)
        else:
            self.me.points.setPos(SCENE_WIDTH - (130 + self.opponent.points.boundingRect().width()), -5)
            self.opponent.points.setPos(130, -5)

    def draw_barrel(self, index):
        self.addItem(self.barrel_pool[index].item)

    def remove_barrel(self, index):
        if self.barrel_pool[index].item.scene() != 0:
            self.removeItem(self.barrel_pool[index].item)

    def clear_scene(self):
        for item in self.items():
            self.removeItem(item)

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

        if self.me.alive:
            if (direction == Direction.LEFT or direction == Direction.RIGHT) and self.me.climbing:
                return

            self.me.latest_direction = direction
            message = json.dumps({ "command": ClientMessage.MOVE.value, "direction": direction.value })
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

    def send_pos_update(self):
        message = json.dumps({"command": ClientMessage.POS.value, "x": self.me.item.x(), "y": self.me.item.y()})
        self.__parent__.socket.send_to_server(message)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return

        if event.key() in {Qt.Key_A, Qt.Key_D, Qt.Key_W, Qt.Key_S} and not event.key() in self.me.keys_pressed:
            self.me.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.me.keys_pressed:
            self.me.keys_pressed.remove(event.key())

