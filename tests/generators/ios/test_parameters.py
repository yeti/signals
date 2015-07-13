import unittest
from signals.generators.ios.parameters import has_id_field, create_id_parameter, generate_relationship_parameters, \
    generate_field_parameters
from signals.parser.schema import DataObject


class ParametersTestCase(unittest.TestCase):
    def test_has_id_field(self):
        request_object = DataObject("$postRequest", {
            "title": "string"
        })
        self.assertFalse(has_id_field(request_object))

        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        self.assertTrue(has_id_field(request_object))

    def test_create_id_parameter(self):
        request_object = DataObject("$postRequest", {
            "title": "string"
        })
        self.assertIsNone(create_id_parameter("/post/", request_object))
        self.assertIsNotNone(create_id_parameter("/post/:id/", request_object))

        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        self.assertIsNone(create_id_parameter("/post/:id/", request_object))

    def test_generate_relationship_parameters(self):
        request_object = DataObject("$userRequest", {
            "profile": "O2O,$profileRequest",
            "tags": "M2M,$tagRequest"
        })
        parameters = generate_relationship_parameters(request_object)
        self.assertEqual(parameters[0].name, "profile")
        self.assertEqual(parameters[0].objc_type, "ProfileRequest")
        self.assertEqual(parameters[1].name, "tags")
        self.assertEqual(parameters[1].objc_type, "NSOrderedSet*")

    def test_generate_field_parameters(self):
        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        parameters = generate_field_parameters(request_object)
        self.assertEqual(parameters[0].name, "id")
        self.assertEqual(parameters[0].objc_type, "NSNumber*")
        self.assertEqual(parameters[1].name, "title")
        self.assertEqual(parameters[1].objc_type, "NSString*")
