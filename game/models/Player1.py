from PyQt5.QtGui import QPixmap

from game.globals import RESOURCES_DIR
from game.models.abstract.Person import Person


class Player1(Person):
    def __init__(self, x, y):
        super().__init__()

        self.current_frame_index = 0
        self.movement_frames_left = [
            QPixmap(RESOURCES_DIR + "mario/move/m_l_2.png"),
            QPixmap(RESOURCES_DIR + "mario/move/m_l_3.png")
        ]
        self.movement_frames_right = [
            QPixmap(RESOURCES_DIR + "mario/move/m_r_2.png"),
            QPixmap(RESOURCES_DIR + "mario/move/m_r_3.png")
        ]
        self.default_frame_left = QPixmap(RESOURCES_DIR + "mario/move/m_l_1.png")
        self.default_frame_right = QPixmap(RESOURCES_DIR + "mario/move/m_r_1.png")
        self.item.setPixmap(self.default_frame_right)
        self.item.setZValue(3)
        self.item.setPos(x, y)
