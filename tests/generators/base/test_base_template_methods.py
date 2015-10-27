import unittest
from signals.generators.base.base_template_methods import BaseTemplateMethods
from signals.parser.api import API, GetAPI
from signals.parser.fields import Field
from signals.parser.schema import DataObject
from tests.utils import create_dynamic_schema


class BaseTemplateMethodsTestCase(unittest.TestCase):
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
        self.assertEqual(BaseTemplateMethods.get_api_request_object(schema.urls[0].patch),
                         schema.urls[0].patch.request_object)

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
        self.assertIsNone(BaseTemplateMethods.get_api_request_object(schema.urls[0].get))

    def test_get_object_name(self):
        data_object = DataObject("$postRequest", {})
        self.assertEqual(BaseTemplateMethods.get_object_name(data_object), "postRequest")
        self.assertEqual(BaseTemplateMethods.get_object_name(data_object, upper_camel_case=True), "PostRequest")

    def test_is_oauth(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertFalse(BaseTemplateMethods.is_oauth(api))

        api.set_authorization({"#meta": API.OAUTH2})
        self.assertTrue(BaseTemplateMethods.is_oauth(api))

    def test_get_media_fields(self):
        fields = [
            Field("title", ["string"]),
            Field("video", ["video"]),
            Field("image", ["image"])
        ]
        media_fields = BaseTemplateMethods.get_media_fields(fields)
        self.assertEqual(len(media_fields), 2)

    def test_is_url(self):
        self.assertTrue(BaseTemplateMethods.is_url("http://test.com"))
        self.assertFalse(BaseTemplateMethods.is_url("Constants.getBaseURL()"))
