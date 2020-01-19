from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.constants import IMAGES_DIR
from common.enums.direction import Direction


class Gorilla(QObject):
    move_signal = pyqtSignal(Direction)
    animation_reset_signal = pyqtSignal(Direction)
    throw_start_signal = pyqtSignal()
    throw_finish_signal = pyqtSignal()

    def __init__(self, x, y):
        super().__init__()
        self.item = QGraphicsPixmapItem()
        self.current_frame_index = 0
        self.movement_frames = [
            QPixmap(IMAGES_DIR + 'gorilla/move/move_1.png'),
            QPixmap(IMAGES_DIR + "gorilla/move/move_2.png")
        ]
        self.throw_frames = [
            QPixmap(IMAGES_DIR + "gorilla/throw/throw_down.png"),
            QPixmap(IMAGES_DIR + "gorilla/throw/throw_up.png")]
        self.item.setPixmap(self.movement_frames[0])
        self.item.setPos(x, y)

        self.move_signal[Direction].connect(self.__move)
        self.animation_reset_signal[Direction].connect(self.__reset_animation)
        self.throw_start_signal.connect(self.__throw_start)
        self.throw_finish_signal.connect(self.__throw_finish)

    """ Handles animations """
    def __animate(self):
        count = len(self.movement_frames)
        if self.current_frame_index + 1 > count - 1:
            self.current_frame_index = 0
        else:
            self.current_frame_index = self.current_frame_index + 1

        self.item.setPixmap(self.movement_frames[self.current_frame_index])

    """ Resets animations """
    def __reset_animation(self, direction: Direction):
        if direction == Direction.LEFT:
            self.item.setPixmap(self.movement_frames[0])
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.movement_frames[1])

    """ Handles movement """
    def __move(self, direction: Direction):
        if direction == Direction.LEFT:
            self.__go_left()
        elif direction == Direction.RIGHT:
            self.__go_right()

    """ Moves gorilla left """
    def __go_left(self):
        self.__animate()
        self.item.moveBy(-40, 0)

    """ Moves gorilla right """
    def __go_right(self):
        self.__animate()
        self.item.moveBy(40, 0)

    """ Starts throwing animation """
    def __throw_start(self):
        self.item.setPixmap(self.throw_frames[0])

    """ Starts throw finish animation """
    def __throw_finish(self):
        self.item.setPixmap(self.throw_frames[1])
