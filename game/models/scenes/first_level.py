from game.globals import PaintObject
from game.models.helper.grid_painter import GridPainter
from game.models.abstract.game_scene import GameScene


class FirstLevel(GameScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPainter(self)

        self.grid_painter.paint_horizontal_line(0, 19, 14, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(3, 6, 10, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(8, 11, 10, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(13, 16, 10, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(9, 10, 8, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(11, 15, 6, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(0, 7, 3, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(9, 14, 3, 0, 0, PaintObject.PLATFORM)
        self.grid_painter.paint_horizontal_line(5, 8, 6, 0, 0, PaintObject.PLATFORM)

        self.grid_painter.paint_vertical_line(2, 10, 13, 0, 0, PaintObject.LADDER)
        self.grid_painter.paint_vertical_line(17, 10, 13, 0, 0, PaintObject.LADDER)
        self.grid_painter.paint_vertical_line(7, 10, 13, 0, 0, PaintObject.LADDER)
        self.grid_painter.paint_vertical_line(12, 10, 13, 0, 0, PaintObject.LADDER)

        self.grid_painter.paint_vertical_line(8, 8, 9, 0, 0, PaintObject.LADDER)
        self.grid_painter.paint_vertical_line(11, 8, 9, 0, 0, PaintObject.LADDER)

        self.grid_painter.paint_vertical_line(10, 6, 7, 0, 0, PaintObject.LADDER)

        self.grid_painter.paint_vertical_line(15, 3, 5, 0, 0, PaintObject.LADDER)
        self.grid_painter.paint_vertical_line(8, 3, 5, 0, 0, PaintObject.LADDER)

        self.grid_painter.paint_one(0, 13, 0, 5, PaintObject.PLAYER_1)
        self.grid_painter.paint_one(19, 13, 13, 5, PaintObject.PLAYER_2)

        self.grid_painter.paint_one(5, 5, 0, 0, PaintObject.PRINCESS)



        # self.draw_item_to_scene(self.barrel_pool[0])
        # self.draw_item_to_scene(self.barrel_pool[1])
        # self.draw_item_to_scene(self.barrel_pool[2])

        self.barrel_thread.start()
        self.players_thread.start()
        self.players_falling_thread.start()
