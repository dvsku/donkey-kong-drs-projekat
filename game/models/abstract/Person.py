from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import *


class Person(QObject):
    move_signal = pyqtSignal(Player, Direction)
    animation_reset = pyqtSignal(Player, Direction)

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()

        self.current_frame_index = 0
        self.movement_frames_left = []
        self.movement_frames_right = []
        self.default_frame_left = None
        self.default_frame_right = None

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
        self.item.moveBy(-PLAYER_MOVE_SPEED_HORIZONTAL, 0)
        self.__parent__.__parent__.cd.check_end_of_screen_horizontal(self.item)

    def go_right(self):
        self.animate(Direction.RIGHT)
        self.item.moveBy(PLAYER_MOVE_SPEED_HORIZONTAL, 0)
        self.__parent__.__parent__.cd.check_end_of_screen_horizontal(self.item)
