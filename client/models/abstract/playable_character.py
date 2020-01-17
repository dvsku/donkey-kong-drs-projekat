from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsPixmapItem

from common.enums.climb_state import ClimbState
from common.enums.direction import Direction


class PlayableCharacter(QObject):
    move_signal = pyqtSignal(Direction)
    animation_reset_signal = pyqtSignal(Direction)
    fall_signal = pyqtSignal()
    climb_up_signal = pyqtSignal(ClimbState)
    climb_down_signal = pyqtSignal(ClimbState)

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.falling = False
        self.climbing = False

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
