from PyQt5.QtGui import QPixmap
from game.globals import IMAGES_DIR
from game.models.abstract.playable_character import PlayableCharacter


class SecondPlayer(PlayableCharacter):
    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.current_frame_index = 0
        self.movement_frames_left = [
            QPixmap(IMAGES_DIR + "second_player/move/move_left_1.png"),
            QPixmap(IMAGES_DIR + "second_player/move/move_left_2.png")
        ]
        self.movement_frames_right = [
            QPixmap(IMAGES_DIR + "second_player/move/move_right_1.png"),
            QPixmap(IMAGES_DIR + "second_player/move/move_right_2.png")
        ]
        self.default_frame_left = QPixmap(IMAGES_DIR + "second_player/idle/idle_left.png")
        self.default_frame_right = QPixmap(IMAGES_DIR + "second_player/idle/idle_right.png")
        self.item.setPixmap(self.default_frame_left)
        self.item.setZValue(3)
        self.item.setPos(x, y)
