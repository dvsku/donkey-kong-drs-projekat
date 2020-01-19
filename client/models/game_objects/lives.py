from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsPixmapItem

from client.constants import IMAGES_DIR


class Lives(QObject):
    set_lives_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.item = QGraphicsPixmapItem()
        self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))
        self.remaining = 3
        self.set_lives_signal[int].connect(self.set_lives)

    def set_lives(self, lives):
        self.remaining = lives
        if self.remaining == 2:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/2zivota.png"))
        elif self.remaining == 1:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/1zivot.png"))
        elif self.remaining == 0:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/0zivota.png"))
