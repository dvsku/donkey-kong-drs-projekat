from client.models.abstract.info_scene import InfoScene


class MatchEnd(InfoScene):
    def __init__(self, parent):
        super().__init__()
        self.__parent__ = parent
