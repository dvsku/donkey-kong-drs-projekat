import sys
from SceneManager import SceneManager
from PyQt5.QtWidgets import QApplication


# creates game window and sets up title and scene manager
class DonkeyKong(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.setApplicationName("Donkey Kong")
        self.sceneManager = SceneManager()


# program entry point
if __name__ == '__main__':
    app = DonkeyKong(sys.argv)
    sys.exit(app.exec_())
