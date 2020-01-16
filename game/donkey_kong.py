import os
import sys

sys.path += [os.path.abspath('..')]
from PyQt5.QtWidgets import QApplication
from game.models.scenes.scene_control import SceneControl


class DonkeyKong(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.setApplicationName("Donkey Kong")
        self.sceneManager = SceneControl(self)
        self.aboutToQuit.connect(self.sceneManager.closing_cleanup)

    def close_game(self):
        self.quit()


# program entry point
if __name__ == '__main__':
    app = DonkeyKong(sys.argv)
    sys.exit(app.exec_())
