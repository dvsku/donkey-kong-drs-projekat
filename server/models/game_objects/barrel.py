class Barrel:
    def __init__(self, index):
        self.index = index
        self.x = None
        self.y = None
        self.drawn = False

    def set_coordinates(self, x, y):
        self.x = x
        self.y = y
