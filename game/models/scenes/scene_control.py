import multiprocessing as mp
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsView
from game.collision_control import CollisionControl
from game.globals import WINDOW_WIDTH, WINDOW_HEIGHT
from game.models.abstract.game_scene import GameScene
from game.models.game_objects.lives import Lives
from game.models.scenes.first_level import FirstLevel
from game.models.scenes.main_menu import MainMenu


class SceneControl(QObject):
    end_game_signal = pyqtSignal()
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.cc_endpoint = None
        self.setup_collision_control()

        self.current_scene = None
        self.lives = []

        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(WINDOW_WIDTH + 3, WINDOW_HEIGHT + 3)
        self.view.show()

        self.view.setBackgroundBrush(QBrush(Qt.black))
        self.end_game_signal.connect(self.end_game)

        self.load_main_menu()

    def setup_collision_control(self):
        parent, child = mp.Pipe()
        CollisionControl(child)
        self.cc_endpoint = parent

    def load_next_level(self):
        pass

    def end_game(self):
        self.load_main_menu()

    def start_game(self):
        self.lives = [Lives(), Lives()]
        self.load_level(1)

    def load_main_menu(self):
        self.scene_swap_cleanup()

        self.current_scene = MainMenu(self)
        self.view.setScene(self.current_scene)

    def load_level(self, index):
        self.scene_swap_cleanup()

        if index == 1:
            self.current_scene = FirstLevel(self)
            self.view.setScene(self.current_scene)

    def scene_swap_cleanup(self):
        if isinstance(self.current_scene, GameScene) and self.current_scene is not None:
            self.current_scene.kill_thread = True

    def closing_cleanup(self):
        self.scene_swap_cleanup()
        self.cc_endpoint.close()

    def close_game(self):
        self.__parent__.close_game()

