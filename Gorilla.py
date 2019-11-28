from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsRectItem


class Gorilla(QGraphicsRectItem):
    def __init__(self, x,y):
        super().__init__()

        self.setRect(x,y,50,100)
        self.setBrush(QBrush(Qt.darkYellow))


    def goLeft(self):
        self.moveBy(-10,0)
        #self.tryMove(-10,0)

    def goRight(self):
        self.moveBy(10,0)