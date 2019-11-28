from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Princeza(QGraphicsPixmapItem):
    def __init__(self, x, y):
        super().__init__()

        self.princeza = QGraphicsPixmapItem()
        self.princeza.setPixmap(QPixmap.fromImage(QImage("resources/princeza.png")))

        self.princeza.setPos(0, 600-40)



