from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Ladder(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap(IMAGES_DIR + "ladder/ladder.png"))
