from game.globals import PaintDirection, PaintObject, Direction, Player
from game.models.helper.grid_painter import GridPainter
from game.models.abstract.game_scene import GameScene


class FirstLevel(GameScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPainter()
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 222, 228, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 231, 237, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 161, 163, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 146, 153, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 176, 178, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 82, 87, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 89, 90, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 92, 97, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 26, 33, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 229, 289, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 230, 290, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 164, 224, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 175, 235, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 81, 161, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 98, 178, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 88, 148, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 91, 151, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 25, 85, PaintDirection.VERTICAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.LADDER, 34, 94, PaintDirection.VERTICAL, 0, -15)

        self.grid_painter.paint_one(self, PaintObject.PRINCESS, 29, 23, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_1, 280, 0, -10)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_2, 299, 13, -10)

        self.players[0].move_signal[Player, Direction].connect(self.update_player_move)
        self.players[0].animation_reset[Player, Direction].connect(self.update_player_reset_animation)
        self.players[0].fall_signal[Player].connect(self.update_player_fall)
        self.players[1].move_signal[Player, Direction].connect(self.update_player_move)
        self.players[1].animation_reset[Player, Direction].connect(self.update_player_reset_animation)
        self.players[1].fall_signal[Player].connect(self.update_player_fall)

        # self.draw_item_to_scene(self.barrel_pool[0])
        # self.draw_item_to_scene(self.barrel_pool[1])
        # self.draw_item_to_scene(self.barrel_pool[2])

        self.barrel_thread.start()
        self.players_thread.start()
        self.players_falling_thread.start()
