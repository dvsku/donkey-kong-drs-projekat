from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsView
from game.globals import WINDOW_WIDTH, WINDOW_HEIGHT, CCMethods
from game.models.abstract.game_scene import GameScene
from game.models.helper.queue_message import Message
from game.models.scenes.first_level import FirstLevel
from game.models.scenes.main_menu import MainMenu


class SceneControl:
    def __init__(self, parent):
        self.__parent__ = parent

        self.current_scene = None

        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(WINDOW_WIDTH + 3, WINDOW_HEIGHT + 3)
        self.view.show()

        self.view.setBackgroundBrush(QBrush(Qt.black))

        self.load_main_menu()

    def load_main_menu(self):
        self.cleanup()

        self.current_scene = MainMenu(self)
        self.view.setScene(self.current_scene)

    def load_level(self, index):
        self.cleanup()

        if index == 1:
            self.current_scene = FirstLevel(self)
            self.view.setScene(self.current_scene)



    def cleanup(self):
        if isinstance(self.current_scene, GameScene) and self.current_scene is not None:
            self.current_scene.kill_thread = True
            self.current_scene.send_queue.put(Message(CCMethods.KILL_PROCESS))
            self.current_scene.recv_queue.get(True)

    def close_game(self):
        self.__parent__.close_game()

