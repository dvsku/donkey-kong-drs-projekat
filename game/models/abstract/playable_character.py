from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import *


class PlayableCharacter(QObject):
    move_signal = pyqtSignal(Direction)
    animation_reset_signal = pyqtSignal(Direction)
    fall_signal = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.falling = False

        self.current_frame_index = 0
        self.movement_frames_left = []
        self.movement_frames_right = []
        self.default_frame_left = None
        self.default_frame_right = None

        self.move_signal[Direction].connect(self.move)
        self.animation_reset_signal[Direction].connect(self.reset_animation)
        self.fall_signal.connect(self.fall)

    def animate(self, direction: Direction):
        count = -1
        if direction == Direction.LEFT:
            count = len(self.movement_frames_left)
        elif direction == Direction.RIGHT:
            count = len(self.movement_frames_right)

        if self.current_frame_index + 1 > count - 1:
            self.current_frame_index = 0
        else:
            self.current_frame_index = self.current_frame_index + 1

        if direction == Direction.LEFT:
            self.item.setPixmap(self.movement_frames_left[self.current_frame_index])
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.movement_frames_right[self.current_frame_index])

    def reset_animation(self, direction: Direction):
        if direction == Direction.LEFT:
            self.item.setPixmap(self.default_frame_left)
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.default_frame_right)

    def move(self, direction: Direction):
        if direction == direction.LEFT:
            self.go_left()
        elif direction == direction.RIGHT:
            self.go_right()
        elif direction == direction.UP:
            self.go_up()
        elif direction == direction.DOWN:
            self.go_down()

    def go_up(self):

        self.moveBy(0, -40)

    def go_down(self):

        self.moveBy(0, 40)

    def go_left(self):
        self.animate(Direction.LEFT)
        self.item.moveBy(-5, 0)

    def go_right(self):
        self.animate(Direction.RIGHT)
        self.item.moveBy(5, 0)

    def fall(self):
        self.item.moveBy(0, 5)
