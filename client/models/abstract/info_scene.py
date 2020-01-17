from PyQt5.QtWidgets import QGraphicsScene


class InfoScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
