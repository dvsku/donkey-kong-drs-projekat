from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from game.globals import *


class InfoScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.keys_pressed = set()

    def draw_background(self):
        background = QGraphicsRectItem()
        background.setRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        background.setBrush(QBrush(Qt.black))
        self.addItem(background)
