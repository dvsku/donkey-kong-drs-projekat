from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from client.globals import IMAGES_DIR, SCENE_WIDTH
from client.models.abstract.info_scene import InfoScene


class WaitingForPlayers(InfoScene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent

        self.opponent_text = QGraphicsPixmapItem()
        self.opponent_text.setPixmap(QPixmap(IMAGES_DIR + "menu/waiting-for-opponent.png"))
        self.opponent_text.setPos((SCENE_WIDTH - 500) / 2, 250)
        self.addItem(self.opponent_text)
