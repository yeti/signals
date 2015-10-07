from datetime import datetime
from inspect import getmembers, isfunction
import shutil
from signals.generators.ios import template_methods
from signals.generators.ios.conversion import sanitize_field_name
from signals.parser.fields import Field
from signals.parser.schema import URL


class ObjectiveCTemplate:
    def __init__(self, build_dir, project_name, jinja2_environment, schema, data_models_path):
        # Command Flags
        self.project_name = project_name
        self.schema = schema  # Is this right?
        self.data_models_path = data_models_path
        # Setup
        self.jinja2_environment = jinja2_environment
        # File Paths
        self.header_file = "{}/{}DataModel.h".format(build_dir, project_name)
        self.implementation_file = "{}/{}DataModel.m".format(build_dir, project_name)

    def process(self):
        self.create_header_file()
        self.create_implementation_file()
        self.copy_data_models()

    def create_header_file(self):
        self.process_template('data_model.h.j2', self.header_file, {})

    def process_template(self, template_name, template_file_path, extra_context):
        template = self.jinja2_environment.get_template(template_name)
        context = {
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'schema': self.schema,
        }
        context.update(extra_context)
        # Registers all methods in template_methods.py with jinja2 for use
        context.update({name: method for name, method in getmembers(template_methods, isfunction)})
        template_output = template.render(**context)
        with open(template_file_path, "w") as output_file:
            output_file.write(template_output)

    def create_implementation_file(self):
        self.process_template('data_model.m.j2', self.implementation_file, {
            'project_name': self.project_name,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'request_objects': self.get_request_objects(self.schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        })

    def copy_data_models(self):
        shutil.copyfile(self.header_file, "{}/DataModel.h".format(self.data_models_path))
        shutil.copyfile(self.implementation_file, "{}/DataModel.m".format(self.data_models_path))

    @staticmethod
    def get_request_objects(data_objects):
        request_objects = []
        for name, data_object in data_objects.iteritems():
            # TODO: Naming request objects as ...Request is not a standard we always keep true
            if 'Request' in name:
                request_objects.append(data_object)
        return request_objects
