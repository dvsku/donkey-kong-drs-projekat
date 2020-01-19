from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem

from client.constants import IMAGES_DIR
from common.enums.climb_state import ClimbState
from common.enums.direction import Direction


class PlayableCharacter(QObject):
    set_lives_signal = pyqtSignal(int)
    move_signal = pyqtSignal(Direction)
    animation_reset_signal = pyqtSignal(Direction)
    fall_signal = pyqtSignal()
    climb_up_signal = pyqtSignal(ClimbState)
    climb_down_signal = pyqtSignal(ClimbState)
    remove_signal = pyqtSignal()
    update_points_signal = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.lives = QGraphicsPixmapItem()
        self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))
        self.lives_remaining = 0

        self.font = QFont()
        self.font.setPointSize(12)
        self.points = QGraphicsTextItem("0")
        self.points.setDefaultTextColor(Qt.white)
        self.points.setFont(self.font)

        self.falling = False
        self.climbing = False
        self.alive = True

        self.starting_x = 0
        self.starting_y = 0

        self.action_keys = []
        self.keys_pressed = set()
        self.latest_direction = None

        self.current_frame_index = 0
        self.movement_frames_left = []
        self.movement_frames_right = []
        self.climb_frames = []
        self.climb_finish_frames = []
        self.default_frame_left = None
        self.default_frame_right = None
        self.default_frame_up = None

        self.move_signal[Direction].connect(self.move)
        self.animation_reset_signal[Direction].connect(self.reset_animation)
        self.fall_signal.connect(self.fall)
        self.climb_up_signal[ClimbState].connect(self.climb_up)
        self.climb_down_signal[ClimbState].connect(self.climb_down)
        self.set_lives_signal[int].connect(self.set_lives)
        self.update_points_signal[int].connect(self.update_points)

    def update_points(self, points: int):
        self.points.setPlainText(str(points))
        self.__parent__.set_points_position()

    def animate(self, direction: Direction, state=False):
        count = -1
        if direction == Direction.LEFT:
            count = len(self.movement_frames_left)
        elif direction == Direction.RIGHT:
            count = len(self.movement_frames_right)
        elif direction == Direction.UP or direction == Direction.DOWN:
            count = len(self.climb_frames)

        if self.current_frame_index + 1 > count - 1:
            self.current_frame_index = 0
        else:
            self.current_frame_index = self.current_frame_index + 1

        if direction == Direction.LEFT:
            self.item.setPixmap(self.movement_frames_left[self.current_frame_index])
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.movement_frames_right[self.current_frame_index])
        elif direction == Direction.UP:
            if state is True:
                self.item.setPixmap(self.climb_finish_frames[self.current_frame_index])
            else:
                self.item.setPixmap(self.climb_frames[self.current_frame_index])
        elif direction == Direction.DOWN:
            if state is True:
                frames = self.climb_finish_frames
                frames.reverse()
                self.item.setPixmap(frames[self.current_frame_index])
            else:
                self.item.setPixmap(self.climb_frames[self.current_frame_index])

    def reset_animation(self, direction: Direction):
        if direction == Direction.LEFT:
            self.item.setPixmap(self.default_frame_left)
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.default_frame_right)
        elif direction == Direction.UP:
            self.item.setPixmap(self.default_frame_up)
        elif direction == Direction.DOWN:
            self.item.setPixmap(self.default_frame_up)

    def move(self, direction: Direction):
        if direction == direction.LEFT:
            self.animate(Direction.LEFT)
            self.item.moveBy(-5, 0)
        elif direction == direction.RIGHT:
            self.animate(Direction.RIGHT)
            self.item.moveBy(5, 0)

    def climb_up(self, climb_state: ClimbState):
        if climb_state == ClimbState.CLIMB:
            self.climbing = True
            self.animate(Direction.UP)
            self.item.moveBy(0, -5)
        elif climb_state == ClimbState.FINISH:
            self.climbing = True
            self.finish_climbing_up()
        elif climb_state == ClimbState.NONE:
            self.climbing = False
            self.reset_animation(Direction.UP)

    def finish_climbing_up(self):
        self.animate(Direction.UP, state=True)
        self.item.moveBy(0, -5)

    def climb_down(self, climb_state: ClimbState):
        if climb_state == ClimbState.CLIMB:
            self.climbing = True
            self.animate(Direction.DOWN)
            self.item.moveBy(0, 5)
        elif climb_state == ClimbState.FINISH:
            self.climbing = True
            self.finish_climbing_down()
        elif climb_state == ClimbState.NONE:
            self.climbing = False
            self.reset_animation(Direction.DOWN)

    def finish_climbing_down(self):
        self.animate(Direction.DOWN, state=True)
        self.item.moveBy(0, 5)

    def fall(self):
        self.item.moveBy(0, 5)

    def set_lives(self, lives: int):
        self.lives_remaining = lives
        if self.lives_remaining == 3:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))
        elif self.lives_remaining == 2:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/2zivota.png"))
        elif self.lives_remaining == 1:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/1zivot.png"))
        elif self.lives_remaining == 0:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/0zivota.png"))
            self.alive = False

        if self.alive:
            self.item.setPos(self.starting_x, self.starting_y)
        else:
            self.__parent__.removeItem(self.item)
