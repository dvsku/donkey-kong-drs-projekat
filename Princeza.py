from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Princeza(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.setPixmap(QPixmap("resources/princeza.png"))
        self.setPos(x, y)



