from game.globals import *
from game.models.game_objects.help_sign import HelpSign
from game.models.game_objects.platform import Platform
from game.models.game_objects.princess import Princess
from game.models.game_objects.ladder import Ladder
from game.models.abstract.game_scene import GameScene
from game.models.game_objects.lives import Lives
from game.models.game_objects.gorilla import Gorilla


class GridPainter:
    def __init__(self, scene: GameScene):
        self.scene = scene

    def paint_one(self, x: int, y: int, offset_x: int, offset_y: int, item: PaintObject):
        if item == PaintObject.PRINCESS:
            self.scene.princess.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                            y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.princess.item)

        elif item == PaintObject.PLAYER_1:
            self.scene.players[0].item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                              y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.players[0].item)
        elif item == PaintObject.PLAYER_2:
            self.scene.players[1].item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                              y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.players[1].item)
        elif item == PaintObject.HELP_SIGN:
            self.scene.help_sign = HelpSign(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                            y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.help_sign)
        elif item == PaintObject.LIVES:
            self.scene.lives = Lives(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                     y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.lives.item)
        elif item == PaintObject.GORILLA:
            self.scene.gorilla.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                           y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.gorilla.item)

    def paint_horizontal_line(self, x1: int, x2: int, y: int, offset_x: int, offset_y: int, item: PaintObject):
        if x2 < x1:
            print("x1 cannot be bigger than x2")
            return

        for i in range((x2 - x1) + 1):
            if item == PaintObject.PLATFORM:
                temp = Platform()
                temp.setPos((i + x1) * SCENE_GRID_BLOCK_WIDTH + offset_x, y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                temp.setZValue(2)
                self.scene.game_objects[i + x1][y] = temp
                self.scene.addItem(self.scene.game_objects[i + x1][y])

    def paint_vertical_line(self, x: int, y1: int, y2: int, offset_x: int, offset_y: int, item: PaintObject):
        if y2 < y1:
            print("y1 cannot be bigger than y2")
            return

        for i in range((y2 - y1) + 1):
            if item == PaintObject.LADDER:
                temp = Ladder()
                temp.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x, (i + y1) * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                temp.setZValue(2)
                self.scene.game_objects[x][i + y1] = temp
                self.scene.addItem(self.scene.game_objects[x][i + y1])
