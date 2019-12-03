from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import RESOURCES_DIR, SCENE_HEIGHT, set_common_data


class Barrel(QObject):
    delete = pyqtSignal(int)

    def __init__(self, parent, index):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.index = index

        self.current_animation_index = 0
        self.animation_frames = [
            QPixmap(RESOURCES_DIR + "barrel/b_1.png"),
            QPixmap(RESOURCES_DIR + "barrel/b_2.png")
        ]
        self.item.setPixmap(self.animation_frames[0])

    def animate(self):
        count = len(self.animation_frames)
        if self.current_animation_index + 1 > count - 1:
            self.current_animation_index = 0
            self.item.setPixmap(self.animation_frames[self.current_animation_index])
        else:
            self.current_animation_index = self.current_animation_index + 1
            self.item.setPixmap(self.animation_frames[self.current_animation_index])

    def check_end_of_screen(self):
        if self.item.pos().y() >= SCENE_HEIGHT - 40:
            self.delete.emit(self.index)

    def check_collision(self):
        if self.calculate_collision() is True:
            print("bure " + str(self.index) + " udarilo princezu")
            self.delete.emit(self.index)

    def calculate_collision(self):
        test = self.item.pos().y()
        test1 = self.__parent__.princess.pos().y()
        if test != test1:
            return False

        princess_position = set()
        barrel_position = set()
        for i in range(40):
            princess_position.add(self.__parent__.princess.pos().x() + i)
            barrel_position.add(self.item.pos().x() + i)

        return set_common_data(princess_position, barrel_position)

    def goDown(self):
        self.animate()
        self.item.moveBy(0, 5)
        self.check_end_of_screen()
        self.check_collision()
