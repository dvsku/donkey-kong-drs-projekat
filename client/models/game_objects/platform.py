from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.constants import IMAGES_DIR


class Platform(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        self.setPixmap(QPixmap(IMAGES_DIR + "platform/platform.png"))
