from PyQt5.QtCore import QBasicTimer, Qt
from PyQt5.QtGui import QPen, QColor, QBrush, QFont
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from game.globals import SCENE_HEIGHT, SCENE_WIDTH, SCENE_GRID_BLOCK_WIDTH, \
    SCENE_GRID_BLOCK_HEIGHT

class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
        self.timer = QBasicTimer()
        self.grid = []
        self.grid_visible = True

        self.game_objects = [None] * (
                    int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH) * int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT))

    def start_scene_loop(self):
        if not self.timer.isActive():
            self.timer.start(16, self)

    def stop_scene_loop(self):
        if self.timer.isActive():
            self.timer.stop()

    def draw_grid(self):
        rows = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)
        columns = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)

        for x in range(0, rows):
            x_coordinate = x * SCENE_GRID_BLOCK_WIDTH
            # draw a line from x_coordinate, 0 to x, SCENE_HEIGHT
            self.grid.append(self.addLine(x_coordinate, 0, x_coordinate, SCENE_HEIGHT, QPen(QColor(255, 255, 255))))

        for y in range(0, columns):
            y_coordinate = y * SCENE_GRID_BLOCK_HEIGHT
            # draw a line from 0, y_coordinate to SCENE_WIDTH, y_coordinate
            self.grid.append(self.addLine(0, y_coordinate, SCENE_WIDTH, y_coordinate, QPen(QColor(255, 255, 255))))

        counter = 0
        for n in range(0, columns):
            for m in range(0, rows):
                text = QGraphicsTextItem(str(counter))
                text.setDefaultTextColor(Qt.white)
                text.setPos(m * SCENE_GRID_BLOCK_HEIGHT, n * SCENE_GRID_BLOCK_WIDTH)
                self.addItem(text)
                self.grid.append(text)
                counter = counter + 1

    def draw_background(self):
        background = QGraphicsRectItem()
        background.setRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        background.setBrush(QBrush(Qt.black))
        self.addItem(background)

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        for line in self.grid:
            line.setVisible(self.grid_visible)

    def update_scene(self):
        pass

    def keyPressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        pass

    def timerEvent(self, event):
        self.update_scene()
