import multiprocessing as mp

from game.globals import *
from game.models.Barrel import Barrel
from game.models.abstract.Person import Person


class CollisionDetection(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)
        self.start()
        print("Collision Detection PID: " + str(self.pid))

    def check_end_of_screen_horizontal(self, item):
        if item.pos().x() <= 0:
            item.setPos(0, item.pos().y())
        elif item.pos().x() >= SCENE_WIDTH - 40:
            item.setPos(SCENE_WIDTH - 40, item.pos().y())

    def check_end_of_screen_vertical(self, y):
        if y >= SCENE_HEIGHT - 40:
            return True

        return False

    def check_barrel_collision(self, barrel: Barrel, player: Person):
        barrel_pos_y = barrel.item.pos().y()
        player_pos_y = player.item.pos().y()
        barrel_pos_x = barrel.item.pos().x()
        player_pos_x = player.item.pos().x()
        barrel_set = set()
        player_set = set()

        if barrel_pos_y != player_pos_y:
            return False

        for i in range(40):
            barrel_set.add(barrel_pos_x + i)

        for i in range(30):
            player_set.add(player_pos_x + 5 + i)

        return set_common_data(barrel_set, player_set)
