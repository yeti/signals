import unittest
from signals.generators.ios.ios_template_methods import iOSTemplateMethods
from signals.parser.fields import Field
from signals.parser.api import GetAPI, API, PatchAPI
from tests.utils import create_dynamic_schema


class iOSTemplateMethodsTestCase(unittest.TestCase):
    def test_get_url_name(self):
        self.assertEqual(iOSTemplateMethods.get_url_name("/post/:id/favorite/"), "PostWithIdFavorite")

    def test_method_name(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(iOSTemplateMethods.method_name(api), "PostWithSuccess")

        api = GetAPI("post/:id/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(iOSTemplateMethods.method_name(api), "PostWithTheID")

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
        self.assertEqual(iOSTemplateMethods.method_name(schema.urls[0].patch), "PostWithBody")

    def test_content_type(self):
        api = GetAPI("post/", {
            "response": {
                "200+": "$postResponse"
            }
        })
        self.assertEqual(iOSTemplateMethods.content_type(api), "RKMIMETypeJSON")

        api.content_type = API.CONTENT_TYPE_FORM
        self.assertEqual(iOSTemplateMethods.content_type(api), "RKMIMETypeFormURLEncoded")

    def test_media_field_check(self):
        fields = [
            Field("video", ["video"]),
            Field("image", ["image"])
        ]
        media_field_statement = iOSTemplateMethods.media_field_check(fields)
        self.assertEqual(media_field_statement, "video != nil || image != nil")
