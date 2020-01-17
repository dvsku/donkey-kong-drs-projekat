from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from client.constants import IMAGES_DIR
from client.models.abstract.playable_character import PlayableCharacter


class SecondPlayer(PlayableCharacter):
    def __init__(self, parent):
        super().__init__(parent)

        self.action_keys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]

        self.current_frame_index = 0
        self.movement_frames_left = [
            QPixmap(IMAGES_DIR + "second_player/move/move_left_1.png"),
            QPixmap(IMAGES_DIR + "second_player/move/move_left_2.png")
        ]
        self.movement_frames_right = [
            QPixmap(IMAGES_DIR + "second_player/move/move_right_1.png"),
            QPixmap(IMAGES_DIR + "second_player/move/move_right_2.png")
        ]
        self.climb_frames = [
            QPixmap(IMAGES_DIR + "second_player/climb/climb_1.png"),
            QPixmap(IMAGES_DIR + "second_player/climb/climb_2.png")
        ]
        self.climb_finish_frames = [
            QPixmap(IMAGES_DIR + "second_player/climb/climb_finish_1.png"),
            QPixmap(IMAGES_DIR + "second_player/climb/climb_finish_2.png")
        ]
        self.default_frame_left = QPixmap(IMAGES_DIR + "second_player/idle/idle_left.png")
        self.default_frame_right = QPixmap(IMAGES_DIR + "second_player/idle/idle_right.png")
        self.default_frame_up = QPixmap(IMAGES_DIR + "second_player/climb/climb_finish_3.png")
        self.item.setPixmap(self.default_frame_left)
        self.item.setZValue(3)
