from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import QGraphicsScene


# abstract class that will contain all scene logic
class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
        self.timer = QBasicTimer()
        self.timer.start(16, self)

    def start_scene_loop(self):
        if not self.timer.isActive():
            self.timer.start(16, self)

    def stop_scene_loop(self):
        if self.timer.isActive():
            self.timer.stop()

    def update_scene(self):
        pass

    def keyPressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        pass

    def timerEvent(self, event):
        self.update_scene()
