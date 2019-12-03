import sys
import os

sys.path += [os.path.abspath('..')]

from PyQt5.QtWidgets import QApplication
from game.SceneManager import SceneManager


class DonkeyKong(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.setApplicationName("Donkey Kong")
        self.sceneManager = SceneManager(self)
        self.aboutToQuit.connect(self.cleanup)

    def cleanup(self):
        self.sceneManager.current_scene.kill_thread = True

    def close_game(self):
        self.quit()


# program entry point
if __name__ == '__main__':
    app = DonkeyKong(sys.argv)
    sys.exit(app.exec_())
