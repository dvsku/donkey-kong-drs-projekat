from PyQt5.QtCore import Qt
from game.globals import PaintDirection, PaintObject
from game.models.Barrel import Barrel
from game.models.Gorilla import Gorilla
from game.models.GridPaint import GridPaint
from game.models.Person import Person
from game.models.Princeza import Princeza
from game.models.abstract.Scene import Scene


class Level1(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.draw_background()
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPaint()
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 180, 188, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.STAIRS, 189, 289, PaintDirection.VERTICAL)

        self.grid_painter.paint_one(self, PaintObject.PRINCESS, 283, -20, -15)

        #self.gorilla = Gorilla(385, 150)
        #self.addItem(self.gorilla)

        self.addItem(self.barrel_pool[0].item)
        self.addItem(self.barrel_pool[1].item)
        self.addItem(self.barrel_pool[2].item)


    def update_scene(self):
        self.barrel_pool[0].goDown()
        self.barrel_pool[1].goDown()
        self.barrel_pool[2].goDown()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_M:
            self.toggle_grid()
            return
        elif event.key() == Qt.Key_Escape:
            self.__parent__.load_main_menu()
            return
        elif not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
