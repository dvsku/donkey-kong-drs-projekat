from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
import random
from Barrel import Barrel
from Gorilla import Gorilla
from Person import Person
from Platforma import Platforma
from Princeza import Princeza
from Scene import Scene
from MenuButton import Button
from constants import SCENE_WIDTH, SCENE_HEIGHT, Direction, State


class MainMenu(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent

        self.draw_background()

        self.foreground = QGraphicsRectItem()
        self.foreground.setZValue(2)
        self.foreground.setRect(-1, -1, SCENE_WIDTH + 2, SCENE_HEIGHT + 2)
        self.foreground.setBrush(QBrush(Qt.black))

        self.logo = QGraphicsPixmapItem()
        self.logo.setPixmap(QPixmap.fromImage(QImage("resources/logo.png")))
        self.logo.setPos((SCENE_WIDTH - 600) / 2, 50)

        self.buttons = [
            Button(self.__parent__.load_level, 1, (SCENE_WIDTH - 250) / 2, SCENE_HEIGHT - 250,
                   "resources/start-normal.png",
                   "resources/start-highlighted.png", State.HIGHLIGHTED),
            Button(self.__parent__.close_game, None, (SCENE_WIDTH - 200) / 2, SCENE_HEIGHT - 175,
                   "resources/quit-normal.png",
                   "resources/quit-highlighted.png", State.NORMAL)
        ]

        # self.addItem(self.foreground)
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

        self.draw_background()
        self.draw_grid()
        self.toggle_grid()
        self.curY = 0

        # platforma


        # self.addItem(Platforma(0, 600 - 40))
        # self.addItem(Platforma(40, 600 - 40))
        # self.addItem(Platforma(80, 600 - 40))
        # self.addItem(Platforma(120, 600 - 40))
        # self.addItem(Platforma(160, 600 - 40))
        # self.addItem(Platforma(200, 600 - 40))
        # self.addItem(Platforma(240, 600 - 40))
        # self.addItem(Platforma(280, 600 - 40))
        # self.addItem(Platforma(320, 600 - 40))
        # self.addItem(Platforma(360, 600 - 40))
        # self.addItem(Platforma(400, 600 - 40))
        # self.addItem(Platforma(440, 600 - 40))
        # self.addItem(Platforma(480, 600 - 40))
        # self.addItem(Platforma(520, 600 - 40))
        # self.addItem(Platforma(560, 600 - 40))
        # self.addItem(Platforma(600, 600 - 40))
        # self.addItem(Platforma(640, 600 - 40))
        # self.addItem(Platforma(680, 600 - 40))
        # self.addItem(Platforma(720, 600 - 40))
        # self.addItem(Platforma(760, 600 - 40))
        # self.addItem(Platforma(800, 600 - 40))
        #
        # self.addItem(Platforma(120, 600-120))
        # self.addItem(Platforma(160, 600 - 120))
        # self.addItem(Platforma(200, 600 - 120))
        # self.addItem(Platforma(240, 600 - 120))
        # self.addItem(Platforma(280, 600 - 120))
        # self.addItem(Platforma(440, 600 - 120))
        # self.addItem(Platforma(480, 600 - 120))
        # self.addItem(Platforma(520, 600 - 120))
        # self.addItem(Platforma(560, 600 - 120))
        # self.addItem(Platforma(600, 600 - 120))
        #
        # self.addItem(Platforma(280, 600 - 200))
        # self.addItem(Platforma(320, 600 - 200))
        # self.addItem(Platforma(360, 600 - 200))
        # self.addItem(Platforma(400, 600 - 200))
        # self.addItem(Platforma(440, 600 - 200))
        # self.addItem(Platforma(600, 600 - 200))
        # self.addItem(Platforma(640, 600 - 200))
        # self.addItem(Platforma(680, 600 - 200))
        # self.addItem(Platforma(720, 600 - 200))
        # self.addItem(Platforma(760, 600 - 200))
        #
        # self.addItem(Platforma(80, 600 - 280))
        # self.addItem(Platforma(120, 600 - 280))
        # self.addItem(Platforma(160, 600 - 280))
        # self.addItem(Platforma(200, 600 - 280))
        # self.addItem(Platforma(240, 600 - 280))
        # self.addItem(Platforma(280, 600 - 280))
        # self.addItem(Platforma(480, 600 - 280))
        # self.addItem(Platforma(520, 600 - 280))
        # self.addItem(Platforma(560, 600 - 280))
        # self.addItem(Platforma(600, 600 - 280))
        #
        # self.addItem(Platforma(280, 600 - 360))
        # self.addItem(Platforma(320, 600 - 360))
        # self.addItem(Platforma(360, 600 - 360))
        # self.addItem(Platforma(400, 600 - 360))
        # self.addItem(Platforma(440, 600 - 360))
        # self.addItem(Platforma(480, 600 - 360))
        #
        # self.addItem(Platforma(80, 600 - 440))
        # self.addItem(Platforma(120, 600 - 440))
        # self.addItem(Platforma(160, 600 - 440))
        # self.addItem(Platforma(200, 600 - 440))
        # self.addItem(Platforma(240, 600 - 440))
        # self.addItem(Platforma(280, 600 - 440))
        # self.addItem(Platforma(480, 600 - 440))
        # self.addItem(Platforma(520, 600 - 440))
        # self.addItem(Platforma(560, 600 - 440))
        # self.addItem(Platforma(600, 600 - 440))
        #
        # self.addItem(Platforma(280, 600 - 520))
        # self.addItem(Platforma(320, 600 - 520))
        # self.addItem(Platforma(360, 600 - 520))
        # self.addItem(Platforma(400, 600 - 520))
        # self.addItem(Platforma(440, 600 - 520))
        # self.addItem(Platforma(480, 600 - 520))

        self.addItem(Princeza())
        self.addItem(Platforma())
        self.addItem(Person())

        self.gorilla = Gorilla(385, 150)
        self.addItem(self.gorilla)
        self.barrel1 = Barrel(420, 230)
        self.addItem(self.barrel1)
        self.barrel2 = Barrel(420, 240)
        self.addItem(self.barrel2)
        self.barrel = Barrel(400, 220)
        self.addItem(self.barrel)

    def update_scene(self):
       # pass
       #fali logika za granice po x-osi
        self.barrel.goDown()
        if random.randint(1, 10) % 2 != 0:
            self.gorilla.goLeft()
        else:
            self.gorilla.goRight()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
