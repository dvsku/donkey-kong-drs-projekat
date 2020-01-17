from common.enums.collision_control_methods import CCMethods


class Message:
    def __init__(self, function: CCMethods, *args):
        self.func = function.value
        self.args = args
