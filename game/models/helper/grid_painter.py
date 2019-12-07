from game.globals import *
from game.models.game_objects.platform import Platform
from game.models.game_objects.princess import Princess
from game.models.game_objects.ladder import Ladder
from game.models.abstract.game_scene import GameScene


class GridPainter:
    def paint_one(self, scene: GameScene, item: PaintObject, block: int, offset_x: int, offset_y: int):
        """
        Used to paint a single object to a game scene
        :param scene: Game scene
        :param item: Game object
        :param block: Block on the grid
        :param offset_x: X axis offset in relation to the previously specified block
        :param offset_y: Y axis offset in relation to the previously specified block
        """
        rows = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)
        columns = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)

        counter = -1
        for n in range(0, columns):
            for m in range(0, rows):
                counter = counter + 1

                if counter == block:
                    if item == PaintObject.PRINCESS:
                        scene.princess = Princess(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                  n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                        scene.addItem(scene.princess)
                    elif item == PaintObject.PLAYER_1:
                        scene.players[0].item.setPos(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                     n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                        scene.addItem(scene.players[0].item)
                    elif item == PaintObject.PLAYER_2:
                        scene.players[1].item.setPos(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                     n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                        scene.addItem(scene.players[1].item)

    def paint_line(self, scene: GameScene, item: PaintObject, from_block: int, to_block: int, direction: PaintDirection,
                   offset_x: int, offset_y: int):

        rows = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)
        columns = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)

        counter = -1
        paint_block = from_block
        for n in range(0, columns):
            for m in range(0, rows):
                counter = counter + 1

                if counter == paint_block:
                    if direction == PaintDirection.HORIZONTAL:
                        if item == PaintObject.PLATFORM:
                            temp_item = Platform()
                            temp_item.setPos(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                             n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                            temp_item.setZValue(2)
                            scene.game_objects[counter] = temp_item
                            scene.addItem(scene.game_objects[counter])
                            if paint_block >= to_block:
                                break

                            paint_block = paint_block + 1

                    if direction == PaintDirection.VERTICAL:
                        if item == PaintObject.LADDER:
                            temp_item = Ladder()
                            temp_item.setPos(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                             n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                            temp_item.setZValue(1)
                            scene.game_objects[counter] = temp_item
                            if paint_block != from_block:
                                scene.addItem(temp_item)
                            if paint_block == to_block:
                                break

                            paint_block = paint_block + rows
