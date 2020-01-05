from multiprocessing import Process

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class HelpSign(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()
        self.invincible = 0
        self.setPixmap(QPixmap(IMAGES_DIR + "princess/help.png"))
        self.setPos(x, y)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(300)

    def timerEvent(self):
        self.invincible += 1

        if self.invincible % 2 == 0:
            # self.setPixmap(QPixmap(IMAGES_DIR + "princess/help_second.png"))
            self.setPixmap(QPixmap(""))
            self.invincible = 0
        else:
            self.setPixmap(QPixmap(IMAGES_DIR + "princess/help.png"))

        self.update()
