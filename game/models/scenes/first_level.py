from game.globals import PaintDirection, PaintObject, Direction, Player
from game.models.helper.grid_painter import GridPainter
from game.models.abstract.game_scene import GameScene


class FirstLevel(GameScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.draw_background()
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPainter()
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 280, 299, PaintDirection.HORIZONTAL, 0, 25)
        self.grid_painter.paint_line(self, PaintObject.PLATFORM, 180, 188, PaintDirection.HORIZONTAL, 0, -15)
        self.grid_painter.paint_line(self, PaintObject.STAIRS, 189, 289, PaintDirection.VERTICAL, 0, -15)

        self.grid_painter.paint_one(self, PaintObject.PRINCESS, 164, 3, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_1, 280, 0, -15)
        self.grid_painter.paint_one(self, PaintObject.PLAYER_2, 299, 0, -15)

        self.players[0].move_signal[Player, Direction].connect(self.update_player_move)
        self.players[0].animation_reset[Player, Direction].connect(self.update_player_reset_animation)
        self.players[1].move_signal[Player, Direction].connect(self.update_player_move)
        self.players[1].animation_reset[Player, Direction].connect(self.update_player_reset_animation)

        self.draw_item_to_scene(self.barrel_pool[0])
        self.draw_item_to_scene(self.barrel_pool[1])
        self.draw_item_to_scene(self.barrel_pool[2])

        self.barrel_thread.start()
        self.players_thread.start()
