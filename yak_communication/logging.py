terminal_colors = {"red": "\033[91m", "reset": "\033[0m"}

class Error(Exception):
    def __init__(self, msg):
        self.msg = terminal_colors["red"] + "ERROR: " + msg + terminal_colors["reset"]

    def __str__(self):
        return repr(self.msg)
