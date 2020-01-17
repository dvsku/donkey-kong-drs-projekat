from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsPixmapItem

from client.constants import IMAGES_DIR


class HelpSign(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()
        self.setPixmap(QPixmap(IMAGES_DIR + "princess/help.png"))
        self.setPos(x, y)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(300)

    def timerEvent(self):
        self.setVisible(not self.isVisible())
        self.update()
