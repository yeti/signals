terminal_colors = {"red": "\033[91m", "reset": "\033[0m"}

class SignalsError(Exception):
    def __init__(self, msg):
        self.msg = "{}ERROR: {}{}".format(terminal_colors["red"], msg, terminal_colors["reset"])

    def __str__(self):
        return repr(self.msg)
