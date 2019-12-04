from PyQt5.QtCore import Qt
from game.globals import PaintDirection, PaintObject, Direction, Player
from game.models.GridPaint import GridPaint
from game.models.abstract.Scene import Scene

import threading
import time

class Level1(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.draw_background()
        self.draw_grid()
        self.toggle_grid()

        self.last_pressed_key = None

        self.barrel_thread = threading.Thread(target=self.barrel_thread_do_work)
        self.barrel_thread.start()

        self.players_thread = threading.Thread(target=self.player_thread_do_work)
        self.players_thread.start()

        self.grid_painter = GridPaint()
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 180, 188, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.STAIRS, 189, 289, PaintDirection.VERTICAL)

        self.grid_painter.paint_one(self, PaintObject.PRINCESS, 184, -20, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_1, 280, 0, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_2, 280, 760, -15)

        self.players[0].move_signal[Player, Direction].connect(self.update_player_move)
        self.players[0].animation_reset[Player, Direction].connect(self.update_player_reset_animation)

        # self.gorilla = Gorilla(385, 150)
        # self.addItem(self.gorilla)

        self.draw_item_to_scene(self.barrel_pool[0])
        self.draw_item_to_scene(self.barrel_pool[1])
        self.draw_item_to_scene(self.barrel_pool[2])

    def barrel_thread_do_work(self):
        while not self.kill_thread:
            for i in range(len(self.barrel_pool)):
                if self.barrel_pool[i].is_drawn:
                    self.barrel_pool[i].modify.emit(i)

            time.sleep(0.025)

    def player_thread_do_work(self):
        while not self.kill_thread:
            if len(self.keys_pressed) != 0:
                if Qt.Key_Left in self.keys_pressed:
                    self.last_pressed_key = Qt.Key_Left
                    self.players[0].move_signal.emit(Player.PLAYER_1, Direction.LEFT)
                elif Qt.Key_Right in self.keys_pressed:
                    self.last_pressed_key = Qt.Key_Right
                    self.players[0].move_signal.emit(Player.PLAYER_1, Direction.RIGHT)
                # elif Qt.Key_A in self.keys_pressed:
                #     self.last_pressed_key = Qt.Key_A
                #     self.players[1].move_signal.emit(Player.PLAYER_2, Direction.LEFT)
                # elif Qt.Key_D in self.keys_pressed:
                #     self.players[1].move_signal.emit(Player.PLAYER_2, Direction.RIGHT)

            else:
                if self.last_pressed_key == Qt.Key_Left:
                    self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.LEFT)
                elif self.last_pressed_key == Qt.Key_Right:
                    self.players[0].animation_reset.emit(Player.PLAYER_1, Direction.RIGHT)
                # elif self.last_pressed_key == Qt.Key_A:
                #     self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.LEFT)
                # elif self.last_pressed_key == Qt.Key_D:
                #     self.players[1].animation_reset.emit(Player.PLAYER_2, Direction.RIGHT)

            time.sleep(0.03)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif event.key() == Qt.Key_Escape:
            self.__parent__.load_main_menu()
            return
        elif not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
