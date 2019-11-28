from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Platforma(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.setPixmap(QPixmap("resources/platforma.png"))
        self.platforma = self.setPos(x, y)


