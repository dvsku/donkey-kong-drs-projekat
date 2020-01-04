from PyQt5.QtCore import QPropertyAnimation, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.globals import IMAGES_DIR


class HelpSign(QGraphicsPixmapItem, QPropertyAnimation):
    def __init__(self, x, y):
        super().__init__()

        self.setPixmap(QPixmap(IMAGES_DIR + "princess/help.png"))
        self.setPos(x, y)
