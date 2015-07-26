terminal_colors = {
    "green": "\033[32m",
    "red": "\033[91m",
    "reset": "\033[0m",
    "yellow": "\033[93m"
}


class SignalsError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return colorize_string("red", "ERROR: {}".format(self.msg))


def colorize_string(color, msg):
    return "{}{}{}".format(terminal_colors[color], msg, terminal_colors["reset"])


def warn(msg):
    print(colorize_string("yellow", msg))


def progress(msg):
    print(colorize_string("green", msg))
