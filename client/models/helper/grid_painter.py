from client.globals import *
from client.models.game_objects.first_player import FirstPlayer
from client.models.game_objects.help_sign import HelpSign
from client.models.game_objects.platform import Platform
from client.models.game_objects.princess import Princess
from client.models.game_objects.ladder import Ladder
from client.models.abstract.game_scene import GameScene
from client.models.game_objects.second_player import SecondPlayer
from common.enums import LayoutBlock


class GridPainter:
    def __init__(self, scene: GameScene):
        self.scene = scene

    def paint_layout(self, layout):
        rows = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)
        columns = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)

        for row in range(rows):
            for column in range(columns):
                if layout[row][column] == LayoutBlock.Platform:
                    temp = Platform()
                    temp.setPos(column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT)
                    self.scene.addItem(temp)
                elif layout[row][column] == LayoutBlock.Ladder:
                    temp = Ladder()
                    temp.setPos(column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT)
                    self.scene.addItem(temp)

    def paint_one(self, x: int, y: int, offset_x: int, offset_y: int, item: PaintObject):
        if item == PaintObject.PRINCESS:
            self.scene.princess = Princess(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                           y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.princess)
        elif item == PaintObject.PLAYER_1:
            if isinstance(self.scene.me, FirstPlayer):
                self.scene.me.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                          y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                self.scene.addItem(self.scene.me.item)
            else:
                self.scene.opponent.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                self.scene.addItem(self.scene.opponent.item)
        elif item == PaintObject.PLAYER_2:
            if isinstance(self.scene.me, SecondPlayer):
                self.scene.me.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                          y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                self.scene.addItem(self.scene.me.item)
            else:
                self.scene.opponent.item.setPos(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                self.scene.addItem(self.scene.opponent.item)
        elif item == PaintObject.HELP_SIGN:
            self.scene.help_sign = HelpSign(x * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                            y * SCENE_GRID_BLOCK_HEIGHT + offset_y)
            self.scene.addItem(self.scene.help_sign)