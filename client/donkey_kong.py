import os
import sys
sys.path += [os.path.abspath('..')]
from PyQt5.QtWidgets import QApplication
from client.models.scenes.scene_control import SceneControl


class DonkeyKong(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.setApplicationName("Donkey Kong")
        if len(args) != 3:
            print("Error: invalid arguments.")
            print("Usage: python donkey_kong.py ip_address port")
            sys.exit()

        ip_address = args[1]
        try:
            port = int(args[2])
        except ValueError:
            print("Error: port has to be a number")
            sys.exit()

        self.scene_control = SceneControl(self, ip_address, port)
        self.scene_control.setup_socket()
        self.scene_control.show_scene()
        self.aboutToQuit.connect(self.__cleanup)

    """ Closes the game """
    def close_game(self):
        sys.exit()

    """ Cleans up running threads and open pipe connections """
    def __cleanup(self):
        self.scene_control.cleanup()

if __name__ == '__main__':
    app = DonkeyKong(sys.argv)
    sys.exit(app.exec_())
