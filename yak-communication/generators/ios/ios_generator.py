from generators.base.base_generator import BaseGenerator
from core_data import write_xml_to_file
from data_model import create_mappings


class iOSGenerator(BaseGenerator):
    def __init__(self, schema, data_models_path, core_data_path):
        super(iOSGenerator, self).__init__(schema)
        self.data_models_path = data_models_path
        self.core_data_path = core_data_path

    def process(self):
        print("Creating data model file")
        # create_mappings(urls, objects)

        if self.core_data_path is not None:
            print("Creating core data file")
            write_xml_to_file(self.core_data_path, self.schema.data_objects)
