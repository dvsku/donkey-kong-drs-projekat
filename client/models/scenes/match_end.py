from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsPixmapItem

from client.constants import IMAGES_DIR
from client.models.abstract.info_scene import InfoScene
from client.models.enums.button_state import ButtonState
from client.models.menu_objects.button import Button
from common.constants import SCENE_WIDTH, SCENE_HEIGHT
from common.enums.direction import Direction
from common.enums.info_scenes import InfoScenes
from common.enums.player import Player


class MatchEnd(InfoScene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent

        self.font = QFont()
        self.font.setPointSize(20)
        self.my_points = QGraphicsTextItem(str(self.__parent__.my_score))
        self.my_points.setDefaultTextColor(Qt.white)
        self.my_points.setFont(self.font)
        self.opponent_points = QGraphicsTextItem(str(self.__parent__.opponent_score))
        self.opponent_points.setDefaultTextColor(Qt.white)
        self.opponent_points.setFont(self.font)
        self.logo = QGraphicsPixmapItem()

        self.logo.setPos((SCENE_WIDTH - 600) / 2, 50)

        if self.__parent__.player == Player.PLAYER_1:
            self.my_points.setPos(50, 250)
            self.opponent_points.setPos(SCENE_WIDTH - (50 + self.opponent_points.boundingRect().width()), 250)
        else:
            self.opponent_points.setPos(50, 250)
            self.my_points.setPos(SCENE_WIDTH - (50 + self.opponent_points.boundingRect().width()), 250)

        self.buttons = [Button(self.__parent__.load_info_scene, InfoScenes.MAIN_MENU.value, (SCENE_WIDTH - 300) / 2, SCENE_HEIGHT - 100,
                               IMAGES_DIR + "menu/continue_highlighted.png", IMAGES_DIR + "menu/continue_highlighted.png",
                               ButtonState.HIGHLIGHTED)]

        if self.__parent__.my_score == self.__parent__.opponent_score:
            self.logo.setPixmap(QPixmap(IMAGES_DIR + "menu/draw.png"))
        elif self.__parent__.my_score > self.__parent__.opponent_score:
            self.logo.setPixmap(QPixmap(IMAGES_DIR + "menu/you_won.png"))
        else:
            self.logo.setPixmap(QPixmap(IMAGES_DIR + "menu/you_lost.png"))

        self.__draw_menu_buttons()
        self.addItem(self.my_points)
        self.addItem(self.opponent_points)
        self.addItem(self.logo)

    """ Handles keyboard presses """
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.__change_button_focus(Direction.UP)
        elif event.key() == Qt.Key_S:
            self.__change_button_focus(Direction.DOWN)
        elif event.key() == Qt.Key_Return:
            self.__execute_button()

    """ Draws buttons in the scene """
    def __draw_menu_buttons(self):
        for button in self.buttons:
            self.addItem(button.graphics_item)

    """ Executes button logic """
    def __execute_button(self):
        for index in range(len(self.buttons)):
            self.buttons[index].execute()

    """ Changes button focus """
    def __change_button_focus(self, direction: Direction):
        if direction is None:
            return

        count = len(self.buttons)
        old_index = -1
        new_index = -1
        for index in range(count):
            if self.buttons[index].state is ButtonState.HIGHLIGHTED:
                old_index = index
                if direction is Direction.UP:
                    if index - 1 > 0:
                        new_index = index - 1
                    else:
                        new_index = 0
                elif direction is Direction.DOWN:
                    if index + 1 > count - 1:
                        new_index = count - 1
                    else:
                        new_index = index + 1

        self.buttons[old_index].set_state(ButtonState.NORMAL)
        self.buttons[new_index].set_state(ButtonState.HIGHLIGHTED)
