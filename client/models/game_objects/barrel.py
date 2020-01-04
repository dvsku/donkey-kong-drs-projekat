from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.globals import IMAGES_DIR


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

        self.draw_signal.connect(self.draw)
        self.remove_signal.connect(self.remove)
        self.fall_signal.connect(self.fall)

    def animate(self):
        count = len(self.animation_frames)
        if self.current_animation_index + 1 > count - 1:
            self.current_animation_index = 0
            self.item.setPixmap(self.animation_frames[self.current_animation_index])
        else:
            self.current_animation_index = self.current_animation_index + 1
            self.item.setPixmap(self.animation_frames[self.current_animation_index])

    def draw(self):
        self.__parent__.draw_barrel(self.index)

    def remove(self):
        self.__parent__.remove_barrel(self.index)

    def fall(self):
        self.animate()
        self.item.moveBy(0, 5)
