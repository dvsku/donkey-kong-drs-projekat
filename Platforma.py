from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem


class Platforma(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap("resources/platforma_dole.png"))
        self.platforma = self.setPos(0, 600-40)


