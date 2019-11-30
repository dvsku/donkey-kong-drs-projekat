from PyQt5.QtCore import Qt
from game.globals import PaintDirection, PaintObject
from game.models.Barrel import Barrel
from game.models.Gorilla import Gorilla
from game.models.GridPaint import GridPaint
from game.models.Person import Person
from game.models.Princeza import Princeza
from game.models.abstract.Scene import Scene


class Level1(Scene):
    def __init__(self):
        super().__init__()

        self.draw_background()
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPaint()
        self.grid_painter.paint(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL)
        self.grid_painter.paint(self, PaintObject.PLATFORM, 180, 188, PaintDirection.HORIZONTAL)
        self.grid_painter.paint(self, PaintObject.STAIRS, 189, 289, PaintDirection.VERTICAL)

        self.addItem(Princeza(400, 600 - 535))

        self.addItem(Person())

        self.gorilla = Gorilla(385, 150)
        self.addItem(self.gorilla)
        self.barrel1 = Barrel(420, 230)
        self.addItem(self.barrel1)
        self.barrel2 = Barrel(420, 240)
        self.addItem(self.barrel2)
        self.barrel = Barrel(400, 220)
        self.addItem(self.barrel)

    def update_scene(self):
        pass

    # fali logika za granice po x-osi
    # self.barrel.goDown()
    # if random.randint(1, 10) % 2 != 0:
    #     self.gorilla.goLeft()
    # else:
    #     self.gorilla.goRight()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
