from enum import Enum
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsObject


class State(Enum):
    NONE = 0
    NORMAL = 1
    HIGHLIGHTED = 2


class Button(QGraphicsObject):
    state_changed = pyqtSignal()
    state = State.NONE

    def __init__(self, func, func_param, x: float, y: float, normal: str, highlight: str, state: State):
        super().__init__()
        self.func = func
        self.func_param = func_param
        self.state_changed.connect(self.state_changed_handler)

        self.normalImage = QPixmap.fromImage(QImage(normal))
        self.highlightImage = QPixmap.fromImage(QImage(highlight))

        self.graphics_item = QGraphicsPixmapItem()
        self.graphics_item.setPos(x, y)
        self.set_state(state)

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        self.state_changed.emit()

    def execute(self):
        if self.func_param is None:
            return self.func()
        else:
            return self.func(self.func_param)

    def state_changed_handler(self):
        if self.get_state() is State.NORMAL:
            self.graphics_item.setPixmap(self.normalImage)
        elif self.get_state() is State.HIGHLIGHTED:
            self.graphics_item.setPixmap(self.highlightImage)
