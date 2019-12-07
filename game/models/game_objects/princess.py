from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Princess(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.setPixmap(QPixmap(IMAGES_DIR + "princess/princess.png"))
        self.setPos(x, y)
