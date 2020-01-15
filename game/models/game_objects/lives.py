from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Lives(QObject):
    remove_signal = pyqtSignal()

    def __init__(self, x, y):
        super().__init__()
        self.item = QGraphicsPixmapItem()
        self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))

        self.broj = 3

        self.item.setPos(x, y)

        # self.lives2 = QPixmap(IMAGES_DIR + "lives/2zivota.png")
        #self.lives1 = QPixmap(IMAGES_DIR + "lives/1zivot.png")
       # self.lives0 = QPixmap(IMAGES_DIR + "lives/0zivota.png")

    def remove_lives(self):
        if self.broj == 2:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/2zivota.png"))
        elif self.broj == 1:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/1zivot.png"))
        elif self.broj == 0:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/0zivota.png"))
        else:
            self.item.setPixmap(QPixmap(IMAGES_DIR + "lives/3zivota.png"))
