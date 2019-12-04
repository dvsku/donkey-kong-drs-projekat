from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from game.globals import *
from game.models.Barrel import Barrel
from game.models.Player1 import Player1
from game.models.Player2 import Player2


class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
        self.grid = []
        self.grid_visible = True

        self.kill_thread = False

        self.barrel_count = 5
        self.barrel_pool = []
        self.init_barrel_pool()

        self.princess = None
        self.players = [Player1(self, 0, 0), Player2(self, 0, 0)]

        self.game_objects = [None] * (
                int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH) * int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT))

    def draw_item_to_scene(self, item):
        item.is_drawn = True
        self.addItem(item.item)

    def remove_item_from_scene(self, item):
        item.is_drawn = False
        self.removeItem(item.item)

    def remove_element_from_scene(self, index: int):
        self.barrel_pool[index].is_drawn = False
        self.removeItem(self.barrel_pool[index].item)

    def update_barrel(self, index: int):
        self.barrel_pool[index].goDown()

    def update_player_move(self, player: Player, direction: Direction):
        if player == Player.PLAYER_1:
            self.players[0].move(direction)
        elif player == Player.PLAYER_2:
            pass

    def update_player_reset_animation(self, player: Player, direction: Direction):
        if player == Player.PLAYER_1:
            self.players[0].reset_animation(direction)
        elif player == Player.PLAYER_2:
            pass

    def init_barrel_pool(self):
        for i in range(self.barrel_count):
            temp = Barrel(self, i)
            temp.item.setPos(i * 80, 220)
            temp.delete[int].connect(self.remove_element_from_scene)
            temp.modify[int].connect(self.update_barrel)
            self.barrel_pool.append(temp)

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

    def keyPressEvent(self, event):
        pass

    def keyReleaseEvent(self, event):
        pass
