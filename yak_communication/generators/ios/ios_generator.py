from yak_communication.generators.base.base_generator import BaseGenerator
from yak_communication.generators.ios.core_data import write_xml_to_file
from yak_communication.generators.ios.data_model import create_mappings


class iOSGenerator(BaseGenerator):
    def __init__(self, schema, data_models_path, core_data_path, project_name):
        super(iOSGenerator, self).__init__(schema)
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path
        self.project_name = project_name

    def process(self):
        print("Creating data model file")
        create_mappings(self.schema.urls, self.schema.data_objects, self.project_name)

        if self.core_data_path is not None:
            print("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)
