from PyQt5.QtWidgets import QGraphicsRectItem


class Person(QGraphicsRectItem):

    def __init__(self):
        super().__init__()

    def go_up(self):

        self.moveBy(0, -40)

    def go_down(self):

        self.moveBy(0, 40)

    def go_left(self):

        self.moveBy(-40, 0)

    def go_right(self):

        self.moveBy(40, 0)