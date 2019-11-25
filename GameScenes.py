from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem
from Scene import Scene

BACKGROUND_WIDTH = 800
BACKGROUND_HEIGHT = 600


class MainMenu(Scene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent

        self.background = QGraphicsRectItem()
        self.background.setRect(-1, -1, BACKGROUND_WIDTH + 2, BACKGROUND_HEIGHT + 2)
        self.background.setBrush(QBrush(Qt.black))

        self.placeholderImage1 = QPixmap.fromImage(QImage("placeholder1.png"))
        self.placeholderImage2 = QPixmap.fromImage(QImage("placeholder2.png"))

        self.start_button = QGraphicsPixmapItem()
        self.start_button.setPixmap(self.placeholderImage2)
        self.start_button.setPos(300, 325)

        self.exit_button = QGraphicsPixmapItem()
        self.exit_button.setPixmap(self.placeholderImage1)
        self.exit_button.setPos(300, 400)

        self.addItem(self.background)
        self.addItem(self.start_button)
        self.addItem(self.exit_button)

        self.current_focus = self.start_button

    def change_button_focus(self):
        if self.current_focus == self.start_button:
            self.current_focus = self.exit_button
            self.start_button.setPixmap(self.placeholderImage1)
            self.exit_button.setPixmap(self.placeholderImage2)
        elif self.current_focus == self.exit_button:
            self.current_focus = self.start_button
            self.start_button.setPixmap(self.placeholderImage2)
            self.exit_button.setPixmap(self.placeholderImage1)

    def update_scene(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.change_button_focus()
        elif event.key() == Qt.Key_Down:
            self.change_button_focus()

    def keyReleaseEvent(self, event):
        pass


class Level1(Scene):
    def __init__(self):
        super().__init__()

        background = QGraphicsRectItem()
        background.setRect(-1, -1, BACKGROUND_WIDTH + 2, BACKGROUND_HEIGHT + 2)
        background.setBrush(QBrush(Qt.green))
        self.addItem(background)

    def update_scene(self):
        pass

    def keyPressEvent(self, event):
        if not event.key() in self.keys_pressed:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
