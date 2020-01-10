from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Princess(QObject):
    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.item = QGraphicsPixmapItem()
        self.item.setPixmap(QPixmap(IMAGES_DIR + "princess/princess.png"))
        # self.item.setZValue(2)
        self.item.setPos(x, y)
