import unittest
from signals.generators.ios.swift.parameters import SwiftParameter
from signals.generators.ios.swift.template_methods import SwiftTemplateMethods
from signals.parser.api import GetAPI
from signals.parser.fields import Field
from tests.utils import create_dynamic_schema


class SwiftTemplateMethodsTestCase(unittest.TestCase):
    def test_swift_method_parameters(self):
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
        parameter_signature = SwiftTemplateMethods.method_parameters(schema.urls[0].patch)
        expected = "body: String, title: String, theID: Int, " \
                   "success: RestKitSuccess, " \
                   "failure: RestKitError"
        self.assertEqual(parameter_signature, expected)

    def test_swift_key_path(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(SwiftTemplateMethods.key_path(api), '"results"')

        api.resource_type = GetAPI.RESOURCE_DETAIL
        self.assertEqual(SwiftTemplateMethods.key_path(api), 'nil')

        api = GetAPI("post/:id/favorite/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(SwiftTemplateMethods.key_path(api), 'nil')

    def test_swift_attribute_mappings(self):
        fields = [
            Field("first_title", ["string"]),
            Field("user_id", ["int"])
        ]
        attribute_mapping_string = SwiftTemplateMethods.attribute_mappings(fields)
        self.assertEqual(attribute_mapping_string, '"first_title": "firstTitle", "user_id": "userId"')

    def test_create_swift_parameter_signature(self):
        parameters = [
            SwiftParameter("title", "String"),
            SwiftParameter("userId", "Int")
        ]
        parameter_signature = SwiftTemplateMethods.create_parameter_signature(parameters)
        self.assertEqual(parameter_signature, "title: String, userId: Int")
