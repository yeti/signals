

class BaseGenerator(object):
    BUILD_DIR = "code"

    def __init__(self, schema):
        self.schema = schema

    def process(self):
        pass
