import json
import re
import sys
from json import JSONDecodeError
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsView
from client.models.scenes.game_scene import GameScene
from client.models.networking.client_socket import ClientSocket
from client.models.scenes.main_menu import MainMenu
from client.models.scenes.match_end import MatchEnd
from client.models.scenes.waiting_for_players import WaitingForPlayers
from common.constants import SCENE_WIDTH, SCENE_HEIGHT
from common.enums.client_message import ClientMessage
from common.enums.climb_state import ClimbState
from common.enums.direction import Direction
from common.enums.info_scenes import InfoScenes
from common.enums.layout import Layouts
from common.enums.player import Player
from common.enums.server_message import ServerMessage


class SceneControl(QObject):
    load_game_scene_signal = pyqtSignal(int, int, int)
    load_info_scene_signal = pyqtSignal(int)

    def __init__(self, parent, ip_address, port):
        super().__init__()
        self.__parent__ = parent
        self.ip_address = ip_address
        self.port = port
        self.current_scene = None
        self.player = None
        self.my_score = 0
        self.opponent_score = 0
        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(SCENE_WIDTH + 3, SCENE_HEIGHT + 3)
        self.view.setBackgroundBrush(QBrush(Qt.black))
        self.socket = None

        self.load_game_scene_signal[int, int, int].connect(self.__load_game_scene)
        self.load_info_scene_signal[int].connect(self.load_info_scene)

        self.load_info_scene(InfoScenes.MAIN_MENU.value)

    """ Tries to connect to server """
    def setup_socket(self):
        try:
            self.socket = ClientSocket(self, self.ip_address, self.port)
        except ConnectionError:
            print("Could not connect to server.")
            sys.exit()

    """ Shows the scene """
    def show_scene(self):
        self.view.show()

    """ Sends a request for a game """
    def find_game(self):
        if self.socket is None:
            self.setup_socket()

        message = json.dumps({ "command": ClientMessage.REQUEST_GAME.value })
        self.socket.send_to_server(message)

    """ Handles server messages """
    def process_socket_message(self, msg):
        messages = re.findall(r'({(.*?)})', msg)
        for message in messages:
            try:
                message = json.loads(message[0])
            except JSONDecodeError:
                return

            self.__process_scene_messages(message)
            self.__process_self_movement_messages(message)
            self.__process_opponent_movement_messages(message)
            self.__process_barrel_messages(message)
            self.__process_gorilla_messages(message)
            self.__process_coin_messages(message)

    """ Stops running threads and closes connection to server """
    def cleanup(self):
        self.__cleanup_scene()

        if self.socket is not None:
            message = json.dumps({ "command": ClientMessage.CLOSE.value })
            self.socket.send_to_server(message)
            self.socket.close()

    """ Closes the game """
    def close_game(self):
        self.__parent__.quit()

    """ Handles scene changes messages """
    def __process_scene_messages(self, message):
        if message['command'] == ServerMessage.LOAD_GAME_SCENE.value:
            self.player = Player(message['player'])
            self.my_score = 0
            self.opponent_score = 0
            self.load_game_scene_signal.emit(message['layout'], message['my_lives'], message['opponent_lives'])
        elif message['command'] == ServerMessage.LOAD_INFO_SCENE.value:
            self.load_info_scene_signal.emit(message['scene'])
        elif message['command'] == ServerMessage.MATCH_ENDED.value:
            self.load_info_scene_signal.emit(InfoScenes.MATCH_END.value)

    """ Handles my movement messages """
    def __process_self_movement_messages(self, message):
        if isinstance(self.current_scene, GameScene):
            if message['command'] == ServerMessage.MOVE.value:
                self.current_scene.me.latest_direction = Direction(message['direction'])
                self.current_scene.me.move_signal.emit(Direction(message['direction']))
            elif message['command'] == ServerMessage.STOP.value:
                if self.current_scene.me.latest_direction is not None:
                    self.current_scene.me.animation_reset_signal.emit(self.current_scene.me.latest_direction)
            elif message['command'] == ServerMessage.FALL.value:
                self.current_scene.me.fall_signal.emit()
            elif message['command'] == ServerMessage.CLIMB_UP.value:
                self.current_scene.me.climb_up_signal.emit(ClimbState(message['climb_state']))
            elif message['command'] == ServerMessage.CLIMB_DOWN.value:
                self.current_scene.me.climb_down_signal.emit(ClimbState(message['climb_state']))
            elif message['command'] == ServerMessage.SET_POINTS.value:
                self.my_score = message['points']
                self.current_scene.me.update_points_signal.emit(message['points'])
            elif message['command'] == ServerMessage.SET_POINTS_OPPONENT.value:
                self.opponent_score = message['points']
                self.current_scene.opponent.update_points_signal.emit(message['points'])

    """ Handles opponent's movement messages """
    def __process_opponent_movement_messages(self, message):
        if isinstance(self.current_scene, GameScene):
            if message['command'] == ServerMessage.MOVE_OPPONENT.value:
                self.current_scene.opponent.latest_direction = Direction(message['direction'])
                self.current_scene.opponent.move_signal.emit(Direction(message['direction']))
            elif message['command'] == ServerMessage.STOP_OPPONENT.value:
                if self.current_scene.opponent.latest_direction is not None:
                    self.current_scene.opponent.animation_reset_signal.emit(self.current_scene.opponent.latest_direction)
            elif message['command'] == ServerMessage.FALL_OPPONENT.value:
                self.current_scene.opponent.fall_signal.emit()
            elif message['command'] == ServerMessage.CLIMB_UP_OPPONENT.value:
                self.current_scene.opponent.climb_up_signal.emit(ClimbState(message['climb_state']))
            elif message['command'] == ServerMessage.CLIMB_DOWN_OPPONENT.value:
                self.current_scene.opponent.climb_down_signal.emit(ClimbState(message['climb_state']))

    """ Handles barrel removal and collision """
    def __process_barrel_messages(self, message):
        if isinstance(self.current_scene, GameScene):
            if message['command'] == ServerMessage.REMOVE_BARREL.value:
                self.current_scene.barrel_pool[message['index']].remove_signal.emit()
            elif message['command'] == ServerMessage.MOVE_BARREL.value:
                self.current_scene.barrel_pool[message['index']].fall_signal.emit()
            elif message['command'] == ServerMessage.HIT.value:
                self.current_scene.barrel_pool[message['index']].remove_signal.emit()
                self.current_scene.me.set_lives_signal.emit(message['lives'])
            elif message['command'] == ServerMessage.OPPONENT_HIT.value:
                self.current_scene.barrel_pool[message['index']].remove_signal.emit()
                self.current_scene.opponent.set_lives_signal.emit(message['lives'])

    """ Handles gorilla movement and throwing """
    def __process_gorilla_messages(self, message):
        if isinstance(self.current_scene, GameScene):
            if message['command'] == ServerMessage.GORILLA_MOVE.value:
                self.current_scene.gorilla.move_signal.emit(Direction(message['direction']))
            elif message['command'] == ServerMessage.GORILLA_THROW_BARREL.value:
                self.current_scene.gorilla.throw_start_signal.emit()
                self.current_scene.barrel_pool[message['index']].item.setPos(message['x'], message['y'])
                self.current_scene.barrel_pool[message['index']].draw_signal.emit()
            elif message['command'] == ServerMessage.GORILLA_HIT.value:
                self.current_scene.me.set_lives_signal.emit(message['lives'])
            elif message['command'] == ServerMessage.GORILLA_HIT_OPPONENT.value:
                self.current_scene.opponent.set_lives_signal.emit(message['lives'])

    """ Handles coin messages """
    def __process_coin_messages(self, message):
        if isinstance(self.current_scene, GameScene):
            if message['command'] == ServerMessage.DRAW_COIN.value:
                self.current_scene.coin.draw_signal.emit(message['x'], message['y'])
            elif message['command'] == ServerMessage.REMOVE_COIN.value:
                self.current_scene.coin.remove_signal.emit()
            elif message['command'] == ServerMessage.EFFECT_GAIN_LIFE.value:
                self.current_scene.me.set_coin_life_signal.emit(message['lives'])
            elif message['command'] == ServerMessage.EFFECT_GAIN_LIFE_OPPONENT.value:
                self.current_scene.opponent.set_coin_life_signal.emit(message['lives'])
            elif message['command'] == ServerMessage.EFFECT_LOSE_LIFE.value:
                self.current_scene.me.set_coin_life_signal.emit(message['lives'])
            elif message['command'] == ServerMessage.EFFECT_LOSE_LIFE_OPPONENT.value:
                self.current_scene.opponent.set_coin_life_signal.emit(message['lives'])

    """ Loads scene layout and sets players lives """
    def __load_game_scene(self, layout, my_lives, opponent_lives):
        if not isinstance(self.current_scene, GameScene):
            self.current_scene = GameScene(self, self.player)
            self.view.setScene(self.current_scene)

        if layout == 1:
            self.current_scene.load_layout_and_start(Layouts.FirstLevel.value)
        elif layout == 2:
            self.current_scene.load_layout_and_start(Layouts.SecondLevel.value)
        elif layout == 3:
            self.current_scene.load_layout_and_start(Layouts.ThirdLevel.value)
        elif layout == 4:
            self.current_scene.load_layout_and_start(Layouts.FourthLevel.value)
        elif layout == 5:
            self.current_scene.load_layout_and_start(Layouts.FifthLevel.value)

        self.current_scene.set_lives(my_lives, opponent_lives)
        self.current_scene.draw_lives()
        self.current_scene.draw_points()

        message = json.dumps({ "command": ClientMessage.READY.value })
        self.socket.send_to_server(message)

    """ Loads an info scene """
    def load_info_scene(self, scene):
        self.__cleanup_scene()
        if scene == InfoScenes.MAIN_MENU.value:
            self.current_scene = MainMenu(self)
        elif scene == InfoScenes.WAITING_FOR_PLAYERS.value:
            self.current_scene = WaitingForPlayers(self)
        elif scene == InfoScenes.MATCH_END.value:
            self.current_scene = MatchEnd(self)

        self.view.setScene(self.current_scene)

    """ Stops running threads """
    def __cleanup_scene(self):
        if isinstance(self.current_scene, GameScene) and self.current_scene is not None:
            self.current_scene.kill_thread = True
