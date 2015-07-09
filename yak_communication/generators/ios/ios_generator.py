import subprocess
from yak_communication.generators.base.base_generator import BaseGenerator
from yak_communication.generators.ios.core_data import write_xml_to_file
from yak_communication.generators.ios.data_model import create_mappings
from yak_communication.logging import SignalsError


class iOSGenerator(BaseGenerator):
    def __init__(self, schema, data_models_path, core_data_path, project_name):
        super(iOSGenerator, self).__init__(schema)
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name

    @staticmethod
    def is_xcode_running():
        return "Xcode.app" in subprocess.check_output(["ps", "-Ax"])

    def process(self):
        if self.core_data_path is not None:
            if self.is_xcode_running():
                raise SignalsError("Must quit Xcode before writing to core data")
            print("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)

        print("Creating data model file")
        create_mappings(self.schema.urls, self.schema.data_objects, self.project_name)
