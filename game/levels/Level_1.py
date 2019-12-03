from PyQt5.QtCore import Qt
from game.globals import PaintDirection, PaintObject, Direction
from game.models.GridPaint import GridPaint
from game.models.abstract.Scene import Scene


class Level1(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.draw_background()
        self.draw_grid()
        self.toggle_grid()

        self.last_pressed_key = None

        self.grid_painter = GridPaint()
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 180, 188, PaintDirection.HORIZONTAL)
        self.grid_painter.paint_line(self, PaintObject.STAIRS, 189, 289, PaintDirection.VERTICAL)

        self.grid_painter.paint_one(self, PaintObject.PRINCESS, 184, -20, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_1, 280, 0, -15)

        # self.gorilla = Gorilla(385, 150)
        # self.addItem(self.gorilla)

        self.addItem(self.barrel_pool[0].item)
        self.addItem(self.barrel_pool[1].item)
        self.addItem(self.barrel_pool[2].item)

    def update_scene(self):
        self.barrel_pool[0].goDown()
        self.barrel_pool[1].goDown()
        self.barrel_pool[2].goDown()

        if Qt.Key_Left in self.keys_pressed:
            self.player1.go_left()
            self.last_pressed_key = Qt.Key_Left
            return
        elif Qt.Key_Right in self.keys_pressed:
            self.player1.go_right()
            self.last_pressed_key = Qt.Key_Right
            return

        if self.last_pressed_key == Qt.Key_Left:
            self.player1.reset_animation(Direction.LEFT)
        elif self.last_pressed_key == Qt.Key_Right:
            self.player1.reset_animation(Direction.RIGHT)

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
