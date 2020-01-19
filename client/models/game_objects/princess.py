from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from client.constants import IMAGES_DIR
from client.models.game_objects.help_sign import HelpSign


class Princess(QObject):
    def __init__(self, parent, x, y):
        super().__init__(parent)

        self.item = QGraphicsPixmapItem()
        self.item.setPixmap(QPixmap(IMAGES_DIR + "princess/princess.png"))
        # self.item.setZValue(2)
        self.item.setPos(x, y)
        parent.addItem(HelpSign(x + 45, y - 35))
