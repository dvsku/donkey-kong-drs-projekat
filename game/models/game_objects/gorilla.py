from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from game.globals import IMAGES_DIR


class Gorilla(QObject):
    def __init__(self, parent):

        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.is_drawn = False

        self.current_animation_index = 0
        self.animation_frames = [
            QPixmap(IMAGES_DIR + "gorilla/move/move_1.png"),
            QPixmap(IMAGES_DIR + "gorilla/move/move_2.png")
        ]
        self.item.setPixmap(self.animation_frames[0])
        self.item.setZValue(4)

    def go_left(self):
        self.moveBy(-10,0)

    def go_right(self):
        self.moveBy(10,0)