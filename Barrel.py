from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsRectItem


class Barrel(QGraphicsRectItem):
    def __init__(self,x,y):
        super().__init__()

        self.setRect(x, y, 20, 10)
        self.setBrush(QBrush(Qt.yellow))

    def goDown(self):

        self.moveBy(0,5)
