from client.models.abstract.game_scene import GameScene
from client.models.enums.paint_object import PaintObject
from client.models.helper.grid_painter import GridPainter
from common.enums.layout import Layouts
from common.enums.player import Player
from common.layout_builder import get_level_layout


class FirstLevel(GameScene):
    def __init__(self, parent, player: Player):
        super().__init__(parent, player)
        self.draw_grid()
        self.toggle_grid()

        self.grid_painter = GridPainter(self)
        self.grid_painter.paint_layout(get_level_layout(Layouts.FirstLevel.value))

        self.grid_painter.paint_one(0, 13, 0, 5, PaintObject.PLAYER_1)
        self.grid_painter.paint_one(19, 13, 13, 5, PaintObject.PLAYER_2)
        self.send_pos_update()

        self.grid_painter.paint_one(5, 5, 0, 0, PaintObject.PRINCESS)
        self.grid_painter.paint_one(6, 4, 0, 0, PaintObject.HELP_SIGN)

        self.move_thread.start()
        # self.pos_update_thread.start()
