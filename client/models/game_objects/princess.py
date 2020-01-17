from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from client.constants import IMAGES_DIR
from client.models.game_objects.help_sign import HelpSign


class Princess(QGraphicsPixmapItem):
    def __init__(self, parent, x, y):
        super().__init__()

        self.setPixmap(QPixmap(IMAGES_DIR + "princess/princess.png"))
        self.setPos(x, y)
        parent.addItem(HelpSign(self.x() + 45, self.y() - 35))
