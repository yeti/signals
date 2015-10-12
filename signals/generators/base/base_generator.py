import os
import shutil


class BaseGenerator(object):
    BUILD_DIR = "signals_code"

    def __init__(self, schema):
        self.schema = schema

    def process(self):
        pass

    @classmethod
    def clear_generated_code_files(cls):
        if os.path.isdir(cls.BUILD_DIR):
            shutil.rmtree(cls.BUILD_DIR)
