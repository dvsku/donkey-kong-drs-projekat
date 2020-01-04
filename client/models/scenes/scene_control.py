from json import JSONDecodeError
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsView
from client.globals import WINDOW_WIDTH, WINDOW_HEIGHT, Direction
from client.models.abstract.game_scene import GameScene
from client.models.networking.client_socket import ClientSocket
from client.models.scenes.first_level import FirstLevel
from client.models.scenes.main_menu import MainMenu
from client.models.scenes.match_end import MatchEnd
from client.models.scenes.waiting_for_players import WaitingForPlayers
from common.enums import ServerMessage, ClientMessage, Scene, MessageFormat, Player
import json


class SceneControl(QObject):
    load_scene_signal = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.current_scene = None

        self.player = None

        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(WINDOW_WIDTH + 3, WINDOW_HEIGHT + 3)
        self.view.show()

        self.view.setBackgroundBrush(QBrush(Qt.black))
        self.socket = None

        self.load_scene_signal[int].connect(self.load_scene)

        self.load_scene(Scene.MAIN_MENU.value)

    def setup_socket(self):
        self.socket = ClientSocket(self)

    def process_socket_message(self, msg):
        try:
            message = json.loads(msg)
        except JSONDecodeError:
            return

        if message['command'] == ServerMessage.CONNECTION_ACK.value:
            msg = MessageFormat.ONLY_COMMAND.value.format(ClientMessage.REQUEST_GAME.value)
            self.socket.send_to_server(msg)

        elif message['command'] == ServerMessage.LOAD_SCENE.value:
            self.player = Player(message['player'])
            self.load_scene_signal.emit(message['scene'])

        elif message['command'] == ServerMessage.MOVE_OPPONENT.value and isinstance(self.current_scene, GameScene):
            self.current_scene.opponent.latest_direction = Direction(message['direction'])
            self.current_scene.opponent.move_signal.emit(Direction(message['direction']))

        elif message['command'] == ServerMessage.STOP_OPPONENT.value and isinstance(self.current_scene, GameScene):
            self.current_scene.opponent.animation_reset_signal.emit(self.current_scene.opponent.latest_direction)

        elif message['command'] == ServerMessage.FALL_OPPONENT.value and isinstance(self.current_scene, GameScene):
            self.current_scene.opponent.fall_signal.emit()

        elif message['command'] == ServerMessage.MOVE.value and isinstance(self.current_scene, GameScene):
            self.current_scene.me.latest_direction = Direction(message['direction'])
            self.current_scene.me.move_signal.emit(Direction(message['direction']))

        elif message['command'] == ServerMessage.STOP.value and isinstance(self.current_scene, GameScene):
            self.current_scene.me.animation_reset_signal.emit(self.current_scene.me.latest_direction)

        elif message['command'] == ServerMessage.FALL.value and isinstance(self.current_scene, GameScene):
            self.current_scene.me.fall_signal.emit()

        elif message['command'] == ServerMessage.DRAW_BARREL.value and isinstance(self.current_scene, GameScene):
            self.current_scene.barrel_pool[message['index']].item.setPos(message['x'], message['y'])
            self.current_scene.barrel_pool[message['index']].draw_signal.emit()

        elif message['command'] == ServerMessage.REMOVE_BARREL.value and isinstance(self.current_scene, GameScene):
            self.current_scene.barrel_pool[message['index']].remove_signal.emit()

        elif message['command'] == ServerMessage.MOVE_BARREL.value and isinstance(self.current_scene, GameScene):
            self.current_scene.barrel_pool[message['index']].fall_signal.emit()

        elif message['command'] == ServerMessage.HIT.value and isinstance(self.current_scene, GameScene):
            self.current_scene.barrel_pool[message['index']].remove_signal.emit()
            # TODO: lose life

        elif message['command'] == ServerMessage.OPPONENT_HIT.value and isinstance(self.current_scene, GameScene):
            self.current_scene.barrel_pool[message['index']].remove_signal.emit()
            # TODO: lose life

        elif message['command'] == ServerMessage.MATCH_ENDED.value:
            self.load_scene_signal.emit(Scene.MATCH_END.value)

    def load_scene(self, index):
        self.cleanup_scene()
        if index == Scene.MAIN_MENU.value:
            self.current_scene = MainMenu(self)
        elif index == Scene.WAITING_FOR_PLAYERS.value:
            self.current_scene = WaitingForPlayers(self)
        elif index == Scene.FIRST_LEVEL.value:
            self.current_scene = FirstLevel(self, self.player)
        elif index == Scene.MATCH_END.value:
            self.current_scene = MatchEnd(self)

        self.view.setScene(self.current_scene)

    def cleanup_scene(self):
        if isinstance(self.current_scene, GameScene) and self.current_scene is not None:
            self.current_scene.kill_thread = True

    def cleanup(self):
        self.cleanup_scene()

        if self.socket is not None:
            msg = MessageFormat.ONLY_COMMAND.value.format(ClientMessage.CLOSE.value)
            self.socket.send_to_server(msg)
            self.socket.close()

    def close_game(self):
        self.__parent__.close_game()
