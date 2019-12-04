from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem

from game.globals import RESOURCES_DIR


class Gorilla(QObject):
    def __init__(self, parent, x,y):

        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.is_drawn = False

        self.current_animation_index = 0
        self.animation_frames = [
            QPixmap(RESOURCES_DIR + "Kong/kongkretanje_1.png"),
            QPixmap(RESOURCES_DIR + "Kong/kongkretanje_2.png")
        ]
        self.item.setPixmap(self.animation_frames[0])
        self.item.setZValue(4)

    def goLeft(self):
        self.moveBy(-10,0)

    def goRight(self):
        self.moveBy(10,0)