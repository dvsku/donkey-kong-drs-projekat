from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
from Scene import Scene
from MenuButton import Button, State

SCENE_WIDTH = 800
SCENE_HEIGHT = 600


class Direction(Enum):
    UP = 1
    DOWN = 2


class MainMenu(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent

        self.background = QGraphicsRectItem()
        self.background.setRect(-1, -1, SCENE_WIDTH + 2, SCENE_HEIGHT + 2)
        self.background.setBrush(QBrush(Qt.black))

        self.logo = QGraphicsPixmapItem()
        self.logo.setPixmap(QPixmap.fromImage(QImage("resources/logo.png")))
        self.logo.setPos((SCENE_WIDTH - 600) / 2, 50)

        self.buttons = [
            Button(self.__parent__.load_level, 1, (SCENE_WIDTH - 250) / 2, SCENE_HEIGHT - 250, "resources/start-normal.png",
                   "resources/start-highlighted.png", State.HIGHLIGHTED),
            Button(self.__parent__.close_game, None, (SCENE_WIDTH - 200) / 2, SCENE_HEIGHT - 175, "resources/quit-normal.png",
                   "resources/quit-highlighted.png", State.NORMAL)
        ]

        self.addItem(self.background)
        self.addItem(self.logo)
        self.draw_menu_buttons()

    def draw_menu_buttons(self):
        for button in self.buttons:
            self.addItem(button.graphics_item)

    def execute_button(self):
        for index in range(len(self.buttons)):
            if self.buttons[index].get_state() is State.HIGHLIGHTED:
                self.buttons[index].execute()

    def change_button_focus(self, direction: Direction):
        if direction is None:
            return

        count = len(self.buttons)
        old_index = -1
        new_index = -1
        for index in range(count):
            if self.buttons[index].get_state() is State.HIGHLIGHTED:
                old_index = index
                if direction is Direction.UP:
                    if index - 1 > 0:
                        new_index = index - 1
                    else:
                        new_index = 0
                elif direction is Direction.DOWN:
                    if index + 1 > count - 1:
                        new_index = count - 1
                    else:
                        new_index = index + 1

        self.buttons[old_index].set_state(State.NORMAL)
        self.buttons[new_index].set_state(State.HIGHLIGHTED)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.change_button_focus(Direction.UP)
        elif event.key() == Qt.Key_Down:
            self.change_button_focus(Direction.DOWN)
        elif event.key() == Qt.Key_Return:
            self.execute_button()


class Level1(Scene):
    def __init__(self):
        super().__init__()

        background = QGraphicsRectItem()
        background.setRect(-1, -1, SCENE_WIDTH + 2, SCENE_HEIGHT + 2)
        background.setBrush(QBrush(Qt.green))
        self.addItem(background)

    def update_scene(self):
        pass

    def keyPressEvent(self, event):
        if not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
