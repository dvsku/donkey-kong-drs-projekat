from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Platforma(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.platforma = QGraphicsPixmapItem()
        self.platforma.setPixmap(QPixmap.fromImage(QImage("resources/platforma.png")))

        self.platforma.setPos(0, 600 - 15)



