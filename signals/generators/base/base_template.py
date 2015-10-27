from datetime import datetime
from inspect import getmembers, isfunction
from signals.parser.schema import URL


class BaseTemplate(object):
    def __init__(self, project_name, schema, data_models_path, jinja2_environment):
        # Command Flags
        self.project_name = project_name
        self.schema = schema
        self.data_models_path = data_models_path
        # Setup
        self.jinja2_environment = jinja2_environment

    def process_template(self, template_name, template_file_path, template_methods, extra_context):
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

    @staticmethod
    def get_request_objects(data_objects):
        request_objects = []
        for name, data_object in data_objects.iteritems():
            # TODO: Naming request objects as ...Request is not a standard we always keep true
            if 'Request' in name:
                request_objects.append(data_object)
        return request_objects
