from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Lives(QObject):
    remove_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.item = QGraphicsPixmapItem()
        self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))
        self.remaining = 3

    def remove_life(self):
        self.remaining -= 1
        if self.remaining == 2:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/2zivota.png"))
        elif self.remaining == 1:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/1zivot.png"))
        elif self.remaining == 0:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/0zivota.png"))
