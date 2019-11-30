from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from game.globals import RESOURCES_DIR


class Stairs(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap(RESOURCES_DIR + "merdevine.png"))
