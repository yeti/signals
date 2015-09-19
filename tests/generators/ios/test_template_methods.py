import unittest
from signals.generators.ios.parameters import Parameter
from signals.parser.schema import DataObject
from signals.parser.fields import Field
from signals.parser.api import GetAPI, API, PatchAPI
from signals.generators.ios.template_methods import is_url, is_oauth, content_type, get_object_name, get_url_name, \
    get_media_fields, media_field_check, key_path, attribute_mappings, get_api_request_object, \
    create_parameter_signature, method_name, method_parameters
from tests.utils import create_dynamic_schema


class TemplateMethodsTestCase(unittest.TestCase):
    def test_method_name(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(method_name(api), "PostWithSuccess")

        api = GetAPI("post/:id/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(method_name(api), "PostWithTheID")

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
        self.assertEqual(method_name(schema.urls[0].patch), "PostWithBody")

    def test_method_parameters(self):
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
        parameter_signature = method_parameters(schema.urls[0].patch)
        expected = "(NSString*)body title:(NSString*)title theID:(NSNumber*)theID " \
                   "success:(void (^)(RKObjectRequestOperation *operation, RKMappingResult *mappingResult))success " \
                   "failure:(void (^)(RKObjectRequestOperation *operation, NSError *error))failure"
        self.assertEqual(parameter_signature, expected)

    def test_key_path(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(key_path(api), '@"results"')

        api.resource_type = GetAPI.RESOURCE_DETAIL
        self.assertEqual(key_path(api), 'nil')

        api = GetAPI("post/:id/favorite/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(key_path(api), 'nil')

    def test_get_object_name(self):
        data_object = DataObject("$postRequest", {})
        self.assertEqual(get_object_name(data_object), "postRequest")
        self.assertEqual(get_object_name(data_object, upper_camel_case=True), "PostRequest")

    def test_get_url_name(self):
        self.assertEqual(get_url_name("/post/:id/favorite/"), "PostWithIdFavorite")

    def test_attribute_mappings(self):
        fields = [
            Field("first_title", ["string"]),
            Field("user_id", ["int"])
        ]
        attribute_mapping_string = attribute_mappings(fields)
        self.assertEqual(attribute_mapping_string, '@"first_title": @"firstTitle", @"user_id": @"userId"')

    def test_is_oauth(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertFalse(is_oauth(api))

        api.set_authorization({"#meta": API.OAUTH2})
        self.assertTrue(is_oauth(api))

    def test_content_type(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(content_type(api), "RKMIMETypeJSON")

        api.content_type = API.CONTENT_TYPE_FORM
        self.assertEqual(content_type(api), "RKMIMETypeFormURLEncoded")

    def test_get_media_fields(self):
        fields = [
            Field("title", ["string"]),
            Field("video", ["video"]),
            Field("image", ["image"])
        ]
        media_fields = get_media_fields(fields)
        self.assertEqual(len(media_fields), 2)

    def test_media_field_check(self):
        fields = [
            Field("video", ["video"]),
            Field("image", ["image"])
        ]
        media_field_statement = media_field_check(fields)
        self.assertEqual(media_field_statement, "video != nil || image != nil")

    def test_is_url(self):
        self.assertTrue(is_url("http://test.com"))
        self.assertFalse(is_url("Constants.getBaseURL()"))

    def test_create_parameter_signature(self):
        parameters = [
            Parameter("title", "NSString*"),
            Parameter("userId", "NSNumber*")
        ]
        parameter_signature = create_parameter_signature(parameters)
        self.assertEqual(parameter_signature, "(NSString*)title userId:(NSNumber*)userId")

    def test_get_api_request_object(self):
        objects_json = {
            '$postRequest': {"body": "string", "title": "string"},
            '$postResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "post/:id/favorites/",
                "patch": {
                    "request": "$postRequest",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertEqual(get_api_request_object(schema.urls[0].patch), schema.urls[0].patch.request_object)

        objects_json = {
            '$followResponse': {"body": "string", "title": "string"}
        }
        urls_json = [
            {
                "url": "follow/",
                "get": {
                    "response": {
                        "200+": "$followResponse"
                    }
                }
            }
        ]
        schema = create_dynamic_schema(objects_json, urls_json)
        self.assertIsNone(get_api_request_object(schema.urls[0].get))
