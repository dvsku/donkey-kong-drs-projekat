from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsObject

from client.models.enums.button_state import ButtonState


class Button(QGraphicsObject):
    state_changed = pyqtSignal()
    state = ButtonState.NONE

    def __init__(self, func, func_param, x: float, y: float, normal: str, highlight: str, state: ButtonState):
        super().__init__()
        self.func = func
        self.func_param = func_param
        self.state_changed.connect(self.state_changed_handler)

        self.normalImage = QPixmap(normal)
        self.highlightImage = QPixmap(highlight)

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
        if self.get_state() is ButtonState.NORMAL:
            self.graphics_item.setPixmap(self.normalImage)
        elif self.get_state() is ButtonState.HIGHLIGHTED:
            self.graphics_item.setPixmap(self.highlightImage)
