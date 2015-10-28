import shutil
from signals.generators.base.base_template import BaseTemplate
from signals.generators.ios.conversion import sanitize_field_name, get_proper_name
from signals.generators.ios.swift.template_methods import SwiftTemplateMethods
from signals.parser.fields import Field


class SwiftTemplate(BaseTemplate):
    def __init__(self, project_name, schema, data_models_path, jinja2_environment, build_dir):
        super(SwiftTemplate, self).__init__(project_name, schema, data_models_path, jinja2_environment)
        # File Paths
        self.data_model_file = "{}/{}DataModel.swift".format(build_dir, project_name)

    def process(self):
        self.create_data_model_file()
        self.copy_data_models()

    def create_data_model_file(self):
        self.process_template('data_model.swift.j2', self.data_model_file, SwiftTemplateMethods, {
            'project_name': self.project_name,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'get_proper_name': get_proper_name,
            'request_objects': self.get_request_objects(self.schema.data_objects),
            'sanitize_field_name': sanitize_field_name,
        })

    def copy_data_models(self):
        shutil.copyfile(self.data_model_file, "{}/DataModel.swift".format(self.data_models_path))
