from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsRectItem
from Scene import Scene

BACKGROUND_WIDTH = 800
BACKGROUND_HEIGHT = 600


class MainMenu(Scene):
    def __init__(self):
        super().__init__()

        background = QGraphicsRectItem()
        background.setRect(-1, -1, BACKGROUND_WIDTH + 2, BACKGROUND_HEIGHT + 2)
        background.setBrush(QBrush(Qt.black))
        self.addItem(background)


class Level1(Scene):
    def __init__(self):
        super().__init__()

        background = QGraphicsRectItem()
        background.setRect(-1, -1, BACKGROUND_WIDTH + 2, BACKGROUND_HEIGHT + 2)
        background.setBrush(QBrush(Qt.blue))
        self.addItem(background)
