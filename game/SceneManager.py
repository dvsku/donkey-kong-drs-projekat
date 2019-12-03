from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView

from game.CollisionDetection import CollisionDetection
from game.globals import WINDOW_WIDTH, WINDOW_HEIGHT
from game.levels.Level_1 import Level1
from game.levels.MainMenu import MainMenu


class SceneManager:
    def __init__(self, parent):
        self.__parent__ = parent

        self.cd = CollisionDetection()
        self.current_scene = None

        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(WINDOW_WIDTH + 3, WINDOW_HEIGHT + 3)
        self.view.show()

        self.load_main_menu()

    def load_main_menu(self):
        if self.current_scene is not None:
            self.current_scene.kill_thread = True

        self.current_scene = MainMenu(self)
        self.view.setScene(self.current_scene)

    def load_level(self, index):
        if self.current_scene is not None:
            self.current_scene.kill_thread = True

        if index == 1:
            self.current_scene = Level1(self)
            self.view.setScene(self.current_scene)

    def close_game(self):
        self.__parent__.close_game()

