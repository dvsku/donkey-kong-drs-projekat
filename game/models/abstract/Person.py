from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import Direction, PLAYER_MOVE_SPEED_HORIZONTAL, SCENE_WIDTH


class Person(QObject):

    def __init__(self):
        super().__init__()

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

    def check_end_of_screen(self):
        if self.item.pos().x() <= 0:
            self.item.setPos(0, self.item.pos().y())
        elif self.item.pos().x() >= SCENE_WIDTH - 40:
            self.item.setPos(SCENE_WIDTH - 40, self.item.pos().y())

    def go_up(self):

        self.moveBy(0, -40)

    def go_down(self):

        self.moveBy(0, 40)

    def go_left(self):
        self.animate(Direction.LEFT)
        self.item.moveBy(-PLAYER_MOVE_SPEED_HORIZONTAL, 0)
        self.check_end_of_screen()

    def go_right(self):
        self.animate(Direction.RIGHT)
        self.item.moveBy(PLAYER_MOVE_SPEED_HORIZONTAL, 0)
        self.check_end_of_screen()
