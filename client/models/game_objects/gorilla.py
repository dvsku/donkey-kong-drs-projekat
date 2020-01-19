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

    def __init__(self, parent, x, y):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()

        self.latest_direction = None
        self.current_direction = None

        self.move_signal[Direction].connect(self.move)
        self.animation_reset_signal[Direction].connect(self.reset_animation)
        self.throw_start_signal.connect(self.throw_start)
        self.throw_finish_signal.connect(self.throw_finish)
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

    def animate(self):
        count = len(self.movement_frames)
        if self.current_frame_index + 1 > count - 1:
            self.current_frame_index = 0
        else:
            self.current_frame_index = self.current_frame_index + 1

        self.item.setPixmap(self.movement_frames[self.current_frame_index])

    def reset_animation(self, direction: Direction):
        if direction == Direction.LEFT:
            self.item.setPixmap(self.movement_frames[0])
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.movement_frames[1])

    def move(self, direction: Direction):
        if direction == Direction.LEFT:
            self.go_left()
        elif direction == Direction.RIGHT:
            self.go_right()

    def go_left(self):
        self.animate()
        self.item.moveBy(-40, 0)

    def go_right(self):
        self.animate()
        self.item.moveBy(40, 0)

    def throw_start(self):
        self.item.setPixmap(self.throw_frames[0])

    def throw_finish(self):
        self.item.setPixmap(self.throw_frames[1])
