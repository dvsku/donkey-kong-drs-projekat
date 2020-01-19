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
        self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/lives_3.png"))
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
        self.keys_pressed = set()
        self.current_frame_index = 0
        self.latest_direction = None
        self.movement_frames_left = []
        self.movement_frames_right = []
        self.climb_frames = []
        self.climb_finish_frames = []
        self.default_frame_left = None
        self.default_frame_right = None
        self.default_frame_up = None

        self.move_signal[Direction].connect(self.__move)
        self.animation_reset_signal[Direction].connect(self.__reset_animation)
        self.fall_signal.connect(self.__fall)
        self.climb_up_signal[ClimbState].connect(self.__climb_up)
        self.climb_down_signal[ClimbState].connect(self.__climb_down)
        self.set_lives_signal[int].connect(self.set_lives)
        self.update_points_signal[int].connect(self.__update_points)

    """ Changes lives image and removes self from scene on 0 lives """
    def set_lives(self, lives: int):
        self.lives_remaining = lives
        if self.lives_remaining == 3:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/lives_3.png"))
        elif self.lives_remaining == 2:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/lives_2.png"))
        elif self.lives_remaining == 1:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/lives_1.png"))
        elif self.lives_remaining == 0:
            self.lives.setPixmap(QPixmap(IMAGES_DIR + "lives/lives_0.png"))
            self.alive = False

        if self.alive:
            self.item.setPos(self.starting_x, self.starting_y)
        else:
            self.__parent__.removeItem(self.item)

    """ Changes points counter in the scene """
    def __update_points(self, points: int):
        self.points.setPlainText(str(points))
        self.__parent__.set_points_position()

    """ Handles movement animations """
    def __animate(self, direction: Direction, state=False):
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

    """ Resets animations to default frame """
    def __reset_animation(self, direction: Direction):
        if direction == Direction.LEFT:
            self.item.setPixmap(self.default_frame_left)
        elif direction == Direction.RIGHT:
            self.item.setPixmap(self.default_frame_right)
        elif direction == Direction.UP:
            self.item.setPixmap(self.default_frame_up)
        elif direction == Direction.DOWN:
            self.item.setPixmap(self.default_frame_up)

    """ Handles movement """
    def __move(self, direction: Direction):
        if direction == direction.LEFT:
            self.__animate(Direction.LEFT)
            self.item.moveBy(-5, 0)
        elif direction == direction.RIGHT:
            self.__animate(Direction.RIGHT)
            self.item.moveBy(5, 0)

    """ Handles climbing up"""
    def __climb_up(self, climb_state: ClimbState):
        if climb_state == ClimbState.CLIMB:
            self.climbing = True
            self.__animate(Direction.UP)
            self.item.moveBy(0, -5)
        elif climb_state == ClimbState.FINISH:
            self.climbing = True
            self.__finish_climbing_up()
        elif climb_state == ClimbState.NONE:
            self.climbing = False
            self.__reset_animation(Direction.UP)

    """ Handles finishing climbing up  """
    def __finish_climbing_up(self):
        self.__animate(Direction.UP, state=True)
        self.item.moveBy(0, -5)

    """ Handles climbing down """
    def __climb_down(self, climb_state: ClimbState):
        if climb_state == ClimbState.CLIMB:
            self.climbing = True
            self.__animate(Direction.DOWN)
            self.item.moveBy(0, 5)
        elif climb_state == ClimbState.FINISH:
            self.climbing = True
            self.__finish_climbing_down()
        elif climb_state == ClimbState.NONE:
            self.climbing = False
            self.__reset_animation(Direction.DOWN)

    """ Handles finishing climbing down """
    def __finish_climbing_down(self):
        self.__animate(Direction.DOWN, state=True)
        self.item.moveBy(0, 5)

    """ Handles falling """
    def __fall(self):
        self.item.moveBy(0, 5)

