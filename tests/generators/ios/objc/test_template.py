from inspect import getmembers, isfunction
import os
import unittest
from datetime import datetime
from jinja2 import PackageLoader
from jinja2 import Environment
from signals.generators.ios.conversion import sanitize_field_name, get_proper_name
from signals.generators.ios.objc.template import ObjectiveCTemplate
from signals.generators.ios.objc.template_methods import ObjectiveCTemplateMethods
from signals.parser.fields import Relationship, Field
from signals.parser.schema import DataObject, Schema, URL
from signals.parser.api import GetAPI, PatchAPI, PostAPI
from tests.utils import create_dynamic_schema


class TemplateTestCase(unittest.TestCase):
    def setUp(self):
        self.jinja2_environment = Environment(loader=PackageLoader('signals.generators.ios', 'templates/objc/'),
                                              extensions=['jinja2.ext.with_'],
                                              trim_blocks=True,
                                              lstrip_blocks=True)

    def assertTemplateEqual(self, template_name, expected_template, context, expected_context=None):
        current_directory = os.path.dirname(__file__)
        expected_file_path = os.path.join(current_directory, "files", expected_template)
        with open(expected_file_path, "r") as expected_template_file:
            template = self.jinja2_environment.get_template(template_name)
            # Registers all methods in template_methods.py with jinja2 for use
            context.update({name: method for name, method in getmembers(ObjectiveCTemplateMethods, isfunction)})
            context.update({'get_proper_name': get_proper_name,
                            'sanitize_field_name': sanitize_field_name
                            })
            template_output = template.render(**context)
            expected_template_out = expected_template_file.read()
            if expected_context:
                # Using %s formatting syntax, since format uses {'s and the outputted code contains many
                expected_template_out = expected_template_out % expected_context
            self.assertEqual(template_output, expected_template_out)

    def test_descriptors_request_template(self):
        objects_json = {
            '$postRequest': {"body": "string", "title": "string"},
            '$postResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "post/:id/",
                "patch": {
                    "request": "$postRequest",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertTemplateEqual('descriptors/request.j2', 'PatchRequestDescriptor.m', {
            'api': schema.urls[0].patch
        })

        urls_json = [
            {
                "url": "post/",
                "post": {
                    "request": "$postRequest",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertTemplateEqual('descriptors/request.j2', 'PostRequestDescriptor.m', {
            'api': schema.urls[0].post
        })

    def test_descriptors_response_template(self):
        objects_json = {
            '$postResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "post/",
                "get": {
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)

        self.assertTemplateEqual('descriptors/response.j2', 'GetResponseDescriptor.m', {
            'api': schema.urls[0].get
        })

    def test_methods_parameters_template(self):
        objects_json = {
            '$postResponse': {"body": "string", "title": "string"},
            "$postParameters": {'user_id': 'int', 'title': 'string'}
        }
        urls_json = [
            {
                "url": "post/",
                "get": {
                    "parameters": "$postParameters",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertTemplateEqual('methods/parameters.j2', 'MethodParameters.m', {
            'api': schema.urls[0].get,
            'schema': schema
        })

    def test_methods_request_template(self):
        objects_json = {
            '$postRequest': {"body": "string", "title": "string"},
            '$postResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "post/",
                "post": {
                    "request": "$postRequest",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertTemplateEqual('methods/request.j2', 'MethodRequest.m', {
            'api': schema.urls[0].post,
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
        })

    def test_methods_request_template_with_media_fields(self):
        objects_json = {
            '$postRequest': {
                'body': 'string',
                'title': 'string',
                'video': 'video',
                'thumbnail': 'image'
            },
            '$postResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "post/",
                "post": {
                    "request": "$postRequest",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertTemplateEqual('methods/request.j2', 'MethodRequestWithMediaFields.m', {
            'api': schema.urls[0].post,
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
        post_object = DataObject('$postResponse', {
            'id': 'int,primarykey',
            'title': 'string',
            'body': 'string'
        })
        user_object = DataObject('$userResponse', {
            'id': 'int,primarykey'
        })
        relationship = Relationship('user', ["M2O", "$userResponse"])
        relationship.related_object = user_object
        self.assertTemplateEqual('relationship_mapping.j2', 'RelationshipMapping.m', {
            'data_object': post_object,
            'relationship': relationship
        })

    def test_data_model_header_template(self):
        schema = Schema("./tests/files/test_schema.json")
        self.assertTemplateEqual('data_model.h.j2', 'DataModel.h', {
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
        }, expected_context=(
            datetime.today().strftime('%m/%d/%Y'),
        ))

    def test_data_model_implementation_template(self):
        schema = Schema("./tests/files/test_schema.json")
        self.assertTemplateEqual('data_model.m.j2', 'DataModel.m', {
            'project_name': "TestProject",
            'schema': schema,
            'VIDEO_FIELD': Field.VIDEO,
            'IMAGE_FIELD': Field.IMAGE,
            'today': datetime.today(),
            'endpoints': URL.URL_ENDPOINTS.keys(),
            'request_objects': ObjectiveCTemplate.get_request_objects(schema.data_objects),
            'sanitize_field_name': sanitize_field_name
        }, expected_context=(
            datetime.today().strftime('%m/%d/%Y'),
        ))
