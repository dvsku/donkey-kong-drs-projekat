import multiprocessing as mp
import threading
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem
from game.collision_control import CollisionControl
from game.globals import *
from game.models.abstract.playable_character import PlayableCharacter
from game.models.game_objects.barrel import Barrel
from game.models.game_objects.first_player import FirstPlayer
from game.models.game_objects.platform import Platform
from game.models.game_objects.second_player import SecondPlayer
from game.models.helper.queue_message import Message


class GameScene(QGraphicsScene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.first_player_keys_pressed = set()
        self.second_player_keys_pressed = set()
        self.first_player_latest_key = None
        self.second_player_latest_key = None
        self.grid = []
        self.grid_visible = True

        self.kill_thread = False

        self.send_queue = mp.Queue()
        self.recv_queue = mp.Queue()
        CollisionControl(self.send_queue, self.recv_queue)

        self.barrel_thread = threading.Thread(target=self.barrel_thread_do_work)
        self.players_thread = threading.Thread(target=self.player_thread_do_work)
        self.players_falling_thread = threading.Thread(target=self.player_falling_thread_do_work)

        self.barrel_count = 5
        self.barrel_pool = []
        self.init_barrel_pool()

        self.princess = None
        self.players = [FirstPlayer(self, 0, 0), SecondPlayer(self, 0, 0)]

        self.game_objects = [None] * (
                int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH) * int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT))

    # region Updates From Signals
    def update_barrel(self, index: int):
        self.barrel_pool[index].go_down()

    def update_player_move(self, player: Player, direction: Direction):
        if player == Player.PLAYER_1:
            self.players[0].move(direction)
        elif player == Player.PLAYER_2:
            self.players[1].move(direction)

    def update_player_reset_animation(self, player: Player, direction: Direction):
        if player == Player.PLAYER_1:
            self.players[0].reset_animation(direction)
        elif player == Player.PLAYER_2:
            self.players[1].reset_animation(direction)

    def update_player_fall(self, player: Player):
        if player == Player.PLAYER_1:
            self.players[0].fall()
        elif player == Player.PLAYER_2:
            self.players[1].fall()

    # endregion

    # region Barrels
    def init_barrel_pool(self):
        for i in range(self.barrel_count):
            temp = Barrel(self, i)
            temp.item.setPos(i * 80, 220)
            temp.delete[int].connect(self.remove_element_from_scene)
            temp.modify[int].connect(self.update_barrel)
            self.barrel_pool.append(temp)

    def draw_item_to_scene(self, item):
        item.is_drawn = True
        self.addItem(item.item)

    def remove_item_from_scene(self, item):
        item.is_drawn = False
        self.removeItem(item.item)

    def remove_element_from_scene(self, index: int):
        self.remove_item_from_scene(self.barrel_pool[index])

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

        counter = 0
        for n in range(0, columns):
            for m in range(0, rows):
                text = QGraphicsTextItem(str(counter))
                text.setDefaultTextColor(Qt.white)
                text.setPos(m * SCENE_GRID_BLOCK_HEIGHT, n * SCENE_GRID_BLOCK_WIDTH)
                self.addItem(text)
                self.grid.append(text)
                counter = counter + 1

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        for line in self.grid:
            line.setVisible(self.grid_visible)

    # endregion

    # region Collision
    def check_barrel_end_of_screen(self, barrel: Barrel):
        self.send_queue.put(Message(
            CCMethods.END_OF_SCREEN_V,
            barrel.item.pos().y(),
        ))
        msg = self.recv_queue.get(True)

        if msg.args[0]:
            barrel.delete.emit(barrel.index)

    def check_barrel_collision(self, barrel: Barrel, player: PlayableCharacter):
        self.send_queue.put(Message(
            CCMethods.BARREL_COLLISION,
            barrel.item.pos().x(),
            barrel.item.pos().y(),
            barrel.item.boundingRect().width(),
            player.item.pos().x(),
            player.item.pos().y()
        ))
        msg = self.recv_queue.get(True)

        if msg.args[0]:
            barrel.delete.emit(barrel.index)

    def check_end_of_screen_left(self, x):
        self.send_queue.put(Message(
            CCMethods.END_OF_SCREEN_L,
            x,
        ))
        msg = self.recv_queue.get()

        return msg.args[0]

    def check_end_of_screen_right(self, x):
        self.send_queue.put(Message(
            CCMethods.END_OF_SCREEN_R,
            x,
        ))
        msg = self.recv_queue.get()

        return msg.args[0]

    def check_falling(self, x, y, direction: Direction):
        ret_value = False

        if direction == Direction.LEFT:
            column = int((x + 20) / 40)
        elif direction == Direction.RIGHT:
            column = int(x / 40)
        else:
            return False

        row = int(y / 40)
        block = column + (int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH) * row)

        if self.game_objects[block] is None:
            ret_value = True
        elif isinstance(self.game_objects[block], Platform):
            if self.game_objects[block].pos().y() != y:
                ret_value = True

        return ret_value

    # endregion

    # region Barrel Thread
    def barrel_thread_do_work(self):
        while not self.kill_thread:
            for i in range(len(self.barrel_pool)):
                if self.barrel_pool[i].is_drawn:
                    self.barrel_pool[i].modify.emit(i)
                    self.check_barrel_end_of_screen(self.barrel_pool[i])
                    self.check_barrel_collision(self.barrel_pool[i], self.players[0])
                    self.check_barrel_collision(self.barrel_pool[i], self.players[1])

            time.sleep(0.025)

    # endregion

    # region Player Thread
    def player_thread_do_work(self):
        while not self.kill_thread:
            if not self.players[0].falling:
                if len(self.first_player_keys_pressed) != 0:
                    self.player_thread_move_first_player()
                else:
                    self.player_thread_reset_animations_first_player()

            if not self.players[1].falling:
                if len(self.second_player_keys_pressed) != 0:
                    self.player_thread_move_second_player()
                else:
                    self.player_thread_reset_animations_second_player()

            time.sleep(0.03)

    def player_thread_move_first_player(self):
        x = self.players[0].item.pos().x()

        if Qt.Key_A in self.first_player_keys_pressed:
            if self.check_end_of_screen_left(x):
                self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.LEFT)
            else:
                self.players[0].move_signal.emit(Player.PLAYER_1, Direction.LEFT)
                self.first_player_latest_key = Qt.Key_A

        elif Qt.Key_D in self.first_player_keys_pressed:
            if self.check_end_of_screen_right(x):
                self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.RIGHT)
            else:
                self.players[0].move_signal.emit(Player.PLAYER_1, Direction.RIGHT)
                self.first_player_latest_key = Qt.Key_D

    def player_thread_move_second_player(self):
        x = self.players[1].item.pos().x()

        if Qt.Key_Left in self.second_player_keys_pressed:
            if self.check_end_of_screen_left(x):
                self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.LEFT)
            else:
                self.players[1].move_signal.emit(Player.PLAYER_2, Direction.LEFT)
                self.second_player_latest_key = Qt.Key_Left

        elif Qt.Key_Right in self.second_player_keys_pressed:
            if self.check_end_of_screen_right(x):
                self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.RIGHT)
            else:
                self.players[1].move_signal.emit(Player.PLAYER_2, Direction.RIGHT)
                self.second_player_latest_key = Qt.Key_Right

    def player_thread_reset_animations_first_player(self):
        if self.first_player_latest_key == Qt.Key_A:
            self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.LEFT)
        elif self.first_player_latest_key == Qt.Key_D:
            self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.RIGHT)

    def player_thread_reset_animations_second_player(self):
        if self.second_player_latest_key == Qt.Key_Left:
            self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.LEFT)
        elif self.second_player_latest_key == Qt.Key_Right:
            self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.RIGHT)

    def player_falling_thread_do_work(self):
        while not self.kill_thread:
            first_player_x = self.players[0].item.pos().x()
            first_player_y = self.players[0].item.pos().y() + 35
            second_player_x = self.players[1].item.pos().x()
            second_player_y = self.players[1].item.pos().y() + 35

            fall = False
            if Qt.Key_A == self.first_player_latest_key:
                fall = self.check_falling(first_player_x, first_player_y, Direction.LEFT)
            elif Qt.Key_D == self.first_player_latest_key:
                fall = self.check_falling(first_player_x, first_player_y, Direction.RIGHT)

            if fall:
                self.players[0].falling = True
                self.players[0].fall_signal.emit(Player.PLAYER_1)
            else:
                self.players[0].falling = False

            fall = False
            if Qt.Key_Left == self.second_player_latest_key:
                fall = self.check_falling(second_player_x, second_player_y, Direction.LEFT)
            elif Qt.Key_Right == self.second_player_latest_key:
                fall = self.check_falling(second_player_x, second_player_y, Direction.RIGHT)

            if fall:
                self.players[1].falling = True
                self.players[1].fall_signal.emit(Player.PLAYER_2)
            else:
                self.players[1].falling = False

            time.sleep(0.015)

    # endregion

    # region KeyPressEvents
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif event.key() == Qt.Key_Escape:
            self.__parent__.load_main_menu()
            return

        if event.key() in {Qt.Key_A, Qt.Key_D, Qt.Key_W,
                           Qt.Key_S} and not event.key() in self.first_player_keys_pressed:
            self.first_player_keys_pressed.add(event.key())

        if event.key() in {Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down} and \
                not event.key() in self.second_player_keys_pressed:
            self.second_player_keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.first_player_keys_pressed:
            self.first_player_keys_pressed.remove(event.key())

        if event.key() in self.second_player_keys_pressed:
            self.second_player_keys_pressed.remove(event.key())

    # endregion
