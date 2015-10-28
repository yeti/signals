from inspect import getmembers, isfunction
import os
import unittest
from datetime import datetime
from jinja2 import Environment, PackageLoader
from signals.generators.ios.conversion import get_proper_name, sanitize_field_name
from signals.generators.ios.swift.template import SwiftTemplate
from signals.generators.ios.swift.template_methods import SwiftTemplateMethods
from signals.parser.fields import Field
from signals.parser.schema import Schema, URL


class SwiftTemplateTestCase(unittest.TestCase):
    # TODO: Still missing a lot of template test files - see ObjC for examples
    def setUp(self):
        self.jinja2_environment = Environment(loader=PackageLoader('signals.generators.ios', 'templates/swift/'),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def assertTemplateEqual(self, template_name, expected_template, context, expected_context=None):
        current_directory = os.path.dirname(__file__)
        expected_file_path = os.path.join(current_directory, "files", expected_template)
        with open(expected_file_path, "r") as expected_template_file:
            template = self.jinja2_environment.get_template(template_name)
            # Registers all methods in template_methods.py with jinja2 for use
            context.update({name: method for name, method in getmembers(SwiftTemplateMethods, isfunction)})
            context.update({'get_proper_name': get_proper_name,
                            'sanitize_field_name': sanitize_field_name
                            })
            template_output = template.render(**context)
            expected_template_out = expected_template_file.read()
            if expected_context:
                # Using %s formatting syntax, since format uses {'s and the outputted code contains many
                expected_template_out = expected_template_out % expected_context
            self.assertEqual(template_output, expected_template_out)

    def test_swift_data_model_implementation_template(self):
        schema = Schema("./tests/files/test_schema.json")
        self.assertTemplateEqual('data_model.swift.j2', 'DataModel.swift', {
            'project_name': "TestProject",
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'request_objects': SwiftTemplate.get_request_objects(schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        }, expected_context=(
            datetime.today().strftime('%m/%d/%Y'),
        ))
