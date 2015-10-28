import unittest
from signals.generators.ios.objc.parameters import ObjCParameter
from signals.generators.ios.objc.template_methods import ObjectiveCTemplateMethods
from signals.parser.api import GetAPI
from signals.parser.fields import Field
from tests.utils import create_dynamic_schema


class TemplateMethodsTestCase(unittest.TestCase):
    def test_objective_c_method_parameters(self):
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
        parameter_signature = ObjectiveCTemplateMethods.method_parameters(schema.urls[0].patch)
        expected = "(NSString*)body title:(NSString*)title theID:(NSNumber*)theID " \
                   "success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success " \
                   "failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"
        self.assertEqual(parameter_signature, expected)

    def test_objective_c_key_path(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(ObjectiveCTemplateMethods.key_path(api), '@"results"')

        api.resource_type = GetAPI.RESOURCE_DETAIL
        self.assertEqual(ObjectiveCTemplateMethods.key_path(api), 'nil')

        api = GetAPI("post/:id/favorite/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(ObjectiveCTemplateMethods.key_path(api), 'nil')

    def test_objective_c_attribute_mappings(self):
        fields = [
            Field("first_title", ["string"]),
            Field("user_id", ["int"])
        ]
        attribute_mapping_string = ObjectiveCTemplateMethods.attribute_mappings(fields)
        self.assertEqual(attribute_mapping_string, '@"first_title": @"firstTitle", @"user_id": @"userId"')

    def test_create_objc_parameter_signature(self):
        parameters = [
            ObjCParameter("title", "NSString*"),
            ObjCParameter("userId", "NSNumber*")
        ]
        parameter_signature = ObjectiveCTemplateMethods.create_parameter_signature(parameters)
        self.assertEqual(parameter_signature, "(NSString*)title userId:(NSNumber*)userId")
