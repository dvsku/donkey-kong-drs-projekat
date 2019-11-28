from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem, QWidget
from PyQt5.uic.properties import QtGui


class Princeza(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap("resources/princeza.png"))
        self.setPos(500, 600-575)



