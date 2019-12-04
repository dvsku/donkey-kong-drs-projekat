from PyQt5.QtGui import QPixmap

from game.globals import RESOURCES_DIR
from game.models.abstract.Person import Person


class Player2(Person):
    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.current_frame_index = 0
        self.movement_frames_left = [
            QPixmap(RESOURCES_DIR + "mario2/m_l_2_2.png"),
            QPixmap(RESOURCES_DIR + "mario2/m_l_3_2.png")
        ]
        self.movement_frames_right = [
            QPixmap(RESOURCES_DIR + "mario2/m_r_2_2.png"),
            QPixmap(RESOURCES_DIR + "mario2/m_r_3_2.png")
        ]
        self.default_frame_left = QPixmap(RESOURCES_DIR + "mario2/m_l_1_2.png")
        self.default_frame_right = QPixmap(RESOURCES_DIR + "mario2/m_r_1_2.png")
        self.item.setPixmap(self.default_frame_left)
        self.item.setZValue(3)
        self.item.setPos(x, y)