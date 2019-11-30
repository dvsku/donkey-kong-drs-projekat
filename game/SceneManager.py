from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from game.globals import WINDOW_WIDTH, WINDOW_HEIGHT
from game.levels.Level_1 import Level1
from game.levels.MainMenu import MainMenu


class SceneManager:
    def __init__(self, parent):
        self.__parent__ = parent
        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(WINDOW_WIDTH + 3, WINDOW_HEIGHT + 3)
        self.view.show()

        self.load_main_menu()

    def load_main_menu(self):
        self.view.setScene(MainMenu(self))
        self.view.scene().start_scene_loop()

    def load_level(self, index):
        if index == 1:
            self.view.setScene(Level1())
            self.view.scene().start_scene_loop()

    def close_game(self):
        self.__parent__.close_game()

