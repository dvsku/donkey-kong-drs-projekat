import time
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from client.constants import IMAGES_DIR


class Coin(QObject):
    draw_signal = pyqtSignal(int, int)
    remove_signal = pyqtSignal()
    animate_signal = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
        self.item = QGraphicsPixmapItem()
        self.drawn = False
        self.current_frame_index = 0
        self.animation_frames = [QPixmap(IMAGES_DIR + "coin/coin_0.png"), QPixmap(IMAGES_DIR + "coin/coin_1.png"),
            QPixmap(IMAGES_DIR + "coin/coin_2.png"), QPixmap(IMAGES_DIR + "coin/coin_3.png"), QPixmap(IMAGES_DIR + "coin/coin_4.png"),
            QPixmap(IMAGES_DIR + "coin/coin_5.png")]
        self.draw_signal[int, int].connect(self.__draw)
        self.remove_signal.connect(self.__remove)
        self.animate_signal.connect(self.__animate)
        self.animate_thread = Thread(target=self.__animate_thread_do_work)
        self.animate_thread.start()

    def __draw(self, x: int, y: int):
        self.item.setPos(x, y)
        self.__parent__.addItem(self.item)
        self.drawn = True

    def __remove(self):
        self.drawn = False
        self.__parent__.removeItem(self.item)

    def __animate(self):
        self.item.setPixmap(self.animation_frames[self.current_frame_index])

    def __animate_thread_do_work(self):
        while not self.__parent__.kill_thread:
            if self.drawn is True:
                count = len(self.animation_frames)
                if self.current_frame_index + 1 > count - 1:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = self.current_frame_index + 1
                    self.animate_signal.emit()

            time.sleep(0.04)
