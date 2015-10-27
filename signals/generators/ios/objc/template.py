import shutil
from signals.generators.base.base_template import BaseTemplate
from signals.generators.ios.conversion import get_proper_name, sanitize_field_name
from signals.generators.ios.objc.template_methods import ObjectiveCTemplateMethods
from signals.parser.fields import Field


class ObjectiveCTemplate(BaseTemplate):
    def __init__(self, project_name, schema, data_models_path, jinja2_environment, build_dir):
        super(ObjectiveCTemplate, self).__init__(project_name, schema, data_models_path, jinja2_environment)
        # File Paths
        self.header_file = "{}/{}DataModel.h".format(build_dir, project_name)
        self.implementation_file = "{}/{}DataModel.m".format(build_dir, project_name)

    def process(self):
        self.create_header_file()
        self.create_implementation_file()
        self.copy_data_models()

    def create_header_file(self):
        self.process_template('data_model.h.j2', self.header_file, ObjectiveCTemplateMethods, {})

    def create_implementation_file(self):
        self.process_template('data_model.m.j2', self.implementation_file, ObjectiveCTemplateMethods, {
            'project_name': self.project_name,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'get_proper_name': get_proper_name,
            'request_objects': self.get_request_objects(self.schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        })

    def copy_data_models(self):
        shutil.copyfile(self.header_file, "{}/DataModel.h".format(self.data_models_path))
        shutil.copyfile(self.implementation_file, "{}/DataModel.m".format(self.data_models_path))
