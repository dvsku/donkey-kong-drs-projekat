from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.constants import IMAGES_DIR


class Barrel(QObject):
    draw_signal = pyqtSignal()
    remove_signal = pyqtSignal()
    fall_signal = pyqtSignal()

    def __init__(self, parent, index):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.index = index

        self.current_animation_index = 0
        self.animation_frames = [
            QPixmap(IMAGES_DIR + "barrel/barrel_falling_1.png"),
            QPixmap(IMAGES_DIR + "barrel/barrel_falling_2.png")
        ]
        self.item.setPixmap(self.animation_frames[0])
        self.item.setZValue(4)

        self.draw_signal.connect(self.__draw)
        self.remove_signal.connect(self.__remove)
        self.fall_signal.connect(self.__fall)

    """ Handles animations """
    def __animate(self):
        count = len(self.animation_frames)
        if self.current_animation_index + 1 > count - 1:
            self.current_animation_index = 0
            self.item.setPixmap(self.animation_frames[self.current_animation_index])
        else:
            self.current_animation_index = self.current_animation_index + 1
            self.item.setPixmap(self.animation_frames[self.current_animation_index])

    """ Draws barrel to scene """
    def __draw(self):
        self.__parent__.draw_barrel(self.index)

    """ Removes barrel from scene """
    def __remove(self):
        self.__parent__.remove_barrel(self.index)

    """ Moves barrel down """
    def __fall(self):
        self.__animate()
        self.item.moveBy(0, 5)
