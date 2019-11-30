from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import RESOURCES_DIR


class Princeza(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.setPixmap(QPixmap(RESOURCES_DIR + "princeza.png"))
        self.setPos(x, y)



