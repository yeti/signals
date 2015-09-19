import unittest
from tests.utils import captured_stdout
from signals.parser.fields import Field, Relationship
from signals.parser.schema import DataObject, Schema, URL
from signals.logging import colorize_string


class SchemaTestCase(unittest.TestCase):
    def test_create_schema(self):
        # Test that generally the schema object was created.
        # Will test individual pieces in unit tests.
        schema = Schema("./tests/files/test_schema.json")
        self.assertEqual(len(schema.data_objects), 3)
        self.assertEqual(len(schema.urls), 2)
        self.assertEqual(schema.schema_path, "./tests/files/test_schema.json")

    def test_create_apis(self):
        schema = Schema("./tests/files/empty_schema.json")
        self.assertEqual(schema.urls, [])
        schema.create_apis([
            {
                "url": "posts/",
                "get": {
                    "#meta": "oauth2,optional",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            },
            {
                "url": "follows/:id/",
                "delete": {
                    "#meta": "oauth2"
                }
            }
        ])
        self.assertEqual(len(schema.urls), 2)
        self.assertEqual(schema.urls[0].url_path, "posts/")

    def test_create_objects(self):
        schema = Schema("./tests/files/empty_schema.json")
        self.assertEqual(schema.data_objects, {})
        schema.create_objects({
            "$resetPasswordRequest": {
                "email": "string"
            },
            "$resetPasswordResponse": {
                "status": "string"
            }
        })
        self.assertEqual(len(schema.data_objects), 2)
        self.assertEqual(schema.data_objects['$resetPasswordRequest'].name, '$resetPasswordRequest')

    def test_create_field(self):
        data_object = DataObject("$testRequest", {})
        self.assertEqual(data_object.fields, [])
        data_object.create_field("username", "string, optional")
        self.assertEqual(len(data_object.fields), 1)
        self.assertEqual(data_object.fields[0].name, "username")
        self.assertEqual(data_object.fields[0].field_type, "string")
        self.assertEqual(data_object.fields[0].optional, True)

    def test_create_relationship(self):
        data_object = DataObject("$testRequest", {})
        self.assertEqual(data_object.relationships, [])
        data_object.create_field("messages", "O2M, $messageResponse")
        self.assertEqual(len(data_object.relationships), 1)
        self.assertEqual(data_object.relationships[0].name, "messages")
        self.assertEqual(data_object.relationships[0].relationship_type, "O2M")
        self.assertEqual(data_object.relationships[0].related_object, "$messageResponse")

    def test_empty_data_object_properties(self):
        data_object = DataObject("$testRequest", {})
        self.assertEqual(data_object.properties(), [])

    def test_data_object_properties(self):
        data_object = DataObject("$testResponse", {
            "username": "string",
            "messages": "O2M,$messageResponse"
        })
        properties = data_object.properties()
        self.assertEqual(len(properties), 2)
        self.assertEqual(properties[0].name, 'username')
        self.assertIsInstance(properties[0], Field)

        self.assertEqual(properties[1].name, 'messages')
        self.assertIsInstance(properties[1], Relationship)

    def test_init_url(self):
        url = URL({
            "url": "posts/",
            "get": {
                "#meta": "oauth2,optional",
                "response": {
                    "200+": "$postResponse"
                }
            }
        })
        self.assertEqual(url.url_path, "posts/")
        self.assertIsNone(url.documentation)
        self.assertIsNone(url.post)
        self.assertIsNotNone(url.get)

    def test_parse_apis(self):
        url = URL({"url": "posts/"})
        self.assertIsNone(url.get)
        url.parse_apis({
            "url": "posts/",
            "get": {
                "#meta": "oauth2,optional",
                "response": {
                    "200+": "$postResponse"
                }
            }
        })
        self.assertIsNotNone(url.get)
        self.assertEqual(url.get.url_path, "posts/")

    def test_validate_json_fails(self):
        url = URL({"url": "posts/"})
        with captured_stdout() as s:
            url.validate_json({
                "url": "posts/",
                "gets": {
                    "#meta": "oauth2,optional",
                    "response": {
                        "200+": "$postResponse"
                    }
                }
            })
            self.assertEqual(s.getvalue().rstrip("\n"),
                             colorize_string("yellow", "Found unsupported attribute, gets, for url: posts/"))
