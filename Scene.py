from PyQt5.QtWidgets import QGraphicsScene

# abstract class that will contain all scene logic
class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
