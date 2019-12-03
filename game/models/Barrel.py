import time
from timeit import default_timer as timer

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import RESOURCES_DIR, SCENE_HEIGHT, set_common_data


class Barrel(QObject):
    delete = pyqtSignal(int)
    modify = pyqtSignal(int)

    def __init__(self, parent, index):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.index = index
        self.is_drawn = False

        self.current_animation_index = 0
        self.animation_frames = [
            QPixmap(RESOURCES_DIR + "barrel/b_1.png"),
            QPixmap(RESOURCES_DIR + "barrel/b_2.png")
        ]
        self.item.setPixmap(self.animation_frames[0])
        self.item.setZValue(4)

    def animate(self):
        count = len(self.animation_frames)
        if self.current_animation_index + 1 > count - 1:
            self.current_animation_index = 0
            self.item.setPixmap(self.animation_frames[self.current_animation_index])
        else:
            self.current_animation_index = self.current_animation_index + 1
            self.item.setPixmap(self.animation_frames[self.current_animation_index])

    def goDown(self):
        self.animate()
        self.item.moveBy(0, 5)

        if self.__parent__.__parent__.cd.check_end_of_screen_vertical(self.item.pos().y()):
            self.delete.emit(self.index)

        if self.__parent__.__parent__.cd.check_barrel_collision(self, self.__parent__.players[0]):
            self.delete.emit(self.index)
