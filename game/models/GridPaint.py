from game.globals import PaintDirection, SCENE_WIDTH, SCENE_GRID_BLOCK_WIDTH, SCENE_HEIGHT, SCENE_GRID_BLOCK_HEIGHT, \
    PaintObject
from game.models.Platforma import Platforma
from game.models.Princeza import Princeza
from game.models.Stairs import Stairs
from game.models.abstract.Scene import Scene


class GridPaint:
    def paint_one(self, scene: Scene, item: PaintObject, block: int, offset_x: int, offset_y):
        rows = int(SCENE_WIDTH / SCENE_GRID_BLOCK_WIDTH)
        columns = int(SCENE_HEIGHT / SCENE_GRID_BLOCK_HEIGHT)

        counter = -1
        for n in range(0, columns):
            for m in range(0, rows):
                counter = counter + 1

                if counter == block:
                    if item == PaintObject.PRINCESS:
                        scene.princess = Princeza(m * SCENE_GRID_BLOCK_WIDTH + offset_x,
                                                  n * SCENE_GRID_BLOCK_HEIGHT + offset_y)
                        scene.addItem(scene.princess)

    def paint_line(self, scene: Scene, item: PaintObject, from_block: int, to_block: int, direction: PaintDirection):
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
                            temp_item = Platforma()
                            temp_item.setPos(m * SCENE_GRID_BLOCK_WIDTH, n * SCENE_GRID_BLOCK_HEIGHT)
                            temp_item.setZValue(2)
                            scene.game_objects[counter] = temp_item
                            scene.addItem(scene.game_objects[counter])
                            if paint_block >= to_block:
                                break

                            paint_block = paint_block + 1

                    if direction == PaintDirection.VERTICAL:
                        if item == PaintObject.STAIRS:
                            temp_item = Stairs()
                            temp_item.setPos(m * SCENE_GRID_BLOCK_WIDTH, n * SCENE_GRID_BLOCK_HEIGHT)
                            temp_item.setZValue(1)
                            scene.game_objects[counter] = temp_item
                            scene.addItem(temp_item)
                            if paint_block == to_block:
                                break

                            paint_block = paint_block + rows
