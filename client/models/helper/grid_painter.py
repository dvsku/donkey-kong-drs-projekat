from client.models.game_objects.first_player import FirstPlayer
from client.models.game_objects.gorilla import Gorilla
from client.models.game_objects.ladder import Ladder
from client.models.game_objects.platform import Platform
from client.models.game_objects.princess import Princess
from client.models.game_objects.second_player import SecondPlayer
from common.constants import SCENE_HEIGHT, SCENE_GRID_BLOCK_HEIGHT, SCENE_WIDTH, SCENE_GRID_BLOCK_WIDTH
from common.enums.layout_block import LayoutBlock


class GridPainter:
    def __init__(self):
        pass

    """ Paints objects inside layout to a scene """
    def paint_layout(self, scene, layout):
        rows = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)
        columns = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)

        for row in range(rows):
            for column in range(columns):
                if layout[row][column] == LayoutBlock.Platform:
                    temp = Platform()
                    temp.setPos(column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT)
                    scene.addItem(temp)
                elif layout[row][column] == LayoutBlock.Ladder:
                    temp = Ladder()
                    temp.setPos(column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT)
                    scene.addItem(temp)
                elif layout[row][column] == LayoutBlock.Player_1:
                    if isinstance(scene.me, FirstPlayer):
                        scene.me.starting_x = column * SCENE_GRID_BLOCK_WIDTH
                        scene.me.starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                        scene.me.item.setPos(scene.me.starting_x, scene.me.starting_y)
                        scene.addItem(scene.me.item)
                    else:
                        scene.opponent.starting_x = column * SCENE_GRID_BLOCK_WIDTH
                        scene.opponent.starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                        scene.opponent.item.setPos(scene.opponent.starting_x, scene.opponent.starting_y)
                        scene.addItem(scene.opponent.item)
                    layout[row][column] = None
                elif layout[row][column] == LayoutBlock.Player_2:
                    if isinstance(scene.me, SecondPlayer):
                        scene.me.starting_x = column * SCENE_GRID_BLOCK_WIDTH + 13
                        scene.me.starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                        scene.me.item.setPos(scene.me.starting_x, scene.me.starting_y)
                        scene.addItem(scene.me.item)
                    else:
                        scene.opponent.starting_x = column * SCENE_GRID_BLOCK_WIDTH + 13
                        scene.opponent.starting_y = row * SCENE_GRID_BLOCK_HEIGHT + 5
                        scene.opponent.item.setPos(scene.opponent.starting_x, scene.opponent.starting_y)
                        scene.addItem(scene.opponent.item)
                    layout[row][column] = None
                elif layout[row][column] == LayoutBlock.Princess:
                    scene.princess = Princess(scene, column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT)
                    scene.addItem(scene.princess.item)
                elif layout[row][column] == LayoutBlock.Gorilla:
                    scene.gorilla = Gorilla(column * SCENE_GRID_BLOCK_WIDTH, row * SCENE_GRID_BLOCK_HEIGHT - 15)
                    scene.addItem(scene.gorilla.item)
