from inspect import getmembers, isfunction
import os
import unittest
from datetime import datetime
from jinja2 import PackageLoader
from jinja2 import Environment
from signals.generators.ios.ios_generator import iOSGenerator
from signals.generators.ios.conversion import sanitize_field_name
from signals.parser.fields import Relationship, Field
from signals.parser.schema import DataObject, Schema, URL
from signals.generators.ios import template_methods
from signals.parser.api import GetAPI, PatchAPI, PostAPI


class TemplateTestCase(unittest.TestCase):
    def setUp(self):
        self.jinja2_environment = Environment(loader=PackageLoader('signals.generators.ios'),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def assertTemplateEqual(self, template_name, expected_template, context):
        current_directory = os.path.dirname(__file__)
        expected_file_path = os.path.join(current_directory, "files", expected_template)
        with open(expected_file_path, "r") as expected_template_file:
            template = self.jinja2_environment.get_template(template_name)
            # Registers all methods in template_methods.py with jinja2 for use
            context.update({name: method for name, method in getmembers(template_methods, isfunction)})
            template_output = template.render(**context)
            expected_template_out = expected_template_file.read()
            self.assertEqual(template_output, expected_template_out)

    def test_descriptors_request_template(self):
        api = PatchAPI("post/:id/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertTemplateEqual('descriptors/request.j2', 'PatchRequestDescriptor.m', {
            'api': api
        })

        api = PostAPI("post/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertTemplateEqual('descriptors/request.j2', 'PostRequestDescriptor.m', {
            'api': api
        })

    def test_descriptors_response_template(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertTemplateEqual('descriptors/response.j2', 'GetResponseDescriptor.m', {
            'api': api
        })

    def test_methods_parameters_template(self):
        api = GetAPI("post/", {
            "parameters": "$postParameters",
            "response": {
                "200+": "$postResponse"
            }
        })
        # Mock schema object
        schema = {
            'data_objects': {
                '$postParameters': DataObject("$postParameters", {
                    'user_id': 'int',
                    'title': 'string'
                })
            }
        }
        self.assertTemplateEqual('methods/parameters.j2', 'MethodParameters.m', {
            'api': api,
            'schema': schema
        })

    def test_methods_request_template(self):
        api = PostAPI("post/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        # Mock schema object
        schema = {
            'data_objects': {
                '$postRequest': DataObject("$postParameters", {
                    'body': 'string',
                    'title': 'string'
                })
            }
        }
        self.assertTemplateEqual('methods/request.j2', 'MethodRequest.m', {
            'api': api,
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
        })

    def test_methods_request_template_with_media_fields(self):
        api = PostAPI("post/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        # Mock schema object
        schema = {
            'data_objects': {
                '$postRequest': DataObject("$postRequest", {
                    'body': 'string',
                    'title': 'string',
                    'video': 'video',
                    'thumbnail': 'image'
                })
            }
        }
        self.assertTemplateEqual('methods/request.j2', 'MethodRequestWithMediaFields.m', {
            'api': api,
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
        })

    def test_methods_send_object_template(self):
        api = PatchAPI("post/:id/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertTemplateEqual('methods/send_object.j2', 'SendObjectWithId.m', {
            'api': api
        })

        api = PostAPI("post/", {
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertTemplateEqual('methods/send_object.j2', 'SendObject.m', {
            'api': api
        })

    def test_api_method_template(self):
        api = GetAPI("post/", {
            "#meta": "oauth2",
            "request": "$postRequest",
            "response": {
                "200+": "$postResponse"
            }
        })
        # Mock schema object
        schema = {
            'data_objects': {
                '$postRequest': DataObject("$postRequest", {
                    'body': 'string',
                    'title': 'string'
                })
            }
        }
        self.assertTemplateEqual('api_method.j2', 'APIMethod.m', {
            'api': api,
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
        })

    def test_entity_mapping_template(self):
        data_object = DataObject('$postResponse', {
            'id': 'int,primarykey',
            'title': 'string',
            'body': 'string'
        })
        self.assertTemplateEqual('entity_mapping.j2', 'EntityMapping.m', {
            'data_object': data_object,
            'sanitize_field_name': sanitize_field_name
        })

    def test_relationship_mapping_template(self):
        self.assertTemplateEqual('relationship_mapping.j2', 'RelationshipMapping.m', {
            'name': '$postResponse',
            'relationship': Relationship('user', ["M2O", "$userResponse"])
        })

    def test_data_model_header_template(self):
        schema = Schema("./tests/files/test_schema.json")
        self.assertTemplateEqual('data_model.h.j2', 'DataModel.h', {
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
        })

    def test_data_model_implementation_template(self):
        schema = Schema("./tests/files/test_schema.json")
        self.assertTemplateEqual('data_model.m.j2', 'DataModel.m', {
            'project_name': "TestProject",
            'api_url': "http://test.com/api/v1/",
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'request_objects': iOSGenerator.get_request_objects(schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        })
