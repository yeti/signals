import unittest
from signals.generators.base.base_parameters import Parameter
from signals.generators.ios.objc_generator.objc_parameters import ObjCParameter
from signals.generators.ios.swift_generator.swift_parameters import SwiftParameter
from signals.parser.fields import Field
from signals.parser.schema import DataObject
from tests.utils import create_dynamic_schema


class ParametersTestCase(unittest.TestCase):
    # TODO: Swift-specific parameters
    def test_has_id_field(self):
        request_object = DataObject("$postRequest", {
            "title": "string"
        })
        self.assertFalse(Parameter.has_id_field(request_object))

        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        self.assertTrue(Parameter.has_id_field(request_object))

    """
    Objective C Parameter Tests
    """
    def test_get_objc_data_type(self):
        array_field = Field("message", ["string", "array"])
        self.assertEqual(ObjCParameter.get_objc_data_type(array_field), "NSArray*")

        text_field = Field("title", ["string", "optional"])
        self.assertEqual(ObjCParameter.get_objc_data_type(text_field), "NSString*")

    def test_create_objc_id_parameter(self):
        request_object = DataObject("$postRequest", {
            "title": "string"
        })
        self.assertIsNone(ObjCParameter.create_id_parameter("/post/", request_object))
        self.assertIsNotNone(ObjCParameter.create_id_parameter("/post/:id/", request_object))

        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        self.assertIsNone(ObjCParameter.create_id_parameter("/post/:id/", request_object))

    def test_generate_objc_relationship_parameters(self):
        schema = create_dynamic_schema({
            "$userRequest": {
                "username": "string",
                "profile": "O2O,$profileRequest",
                "tags": "M2M,$tagRequest"
            },
            "$profileRequest": {},
            "$tagRequest": {}
        }, [])
        request_object = schema.data_objects['$userRequest']
        parameters = ObjCParameter.generate_relationship_parameters(request_object)
        self.assertEqual(parameters[0].name, "profile")
        self.assertEqual(parameters[0].objc_type, "ProfileRequest")
        self.assertEqual(parameters[1].name, "tags")
        self.assertEqual(parameters[1].objc_type, "NSOrderedSet*")

    def test_generate_objc_field_parameters(self):
        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string",
            "tags": "M2M,$tagRequest"
        })
        parameters = ObjCParameter.generate_field_parameters(request_object)
        self.assertEqual(parameters[0].name, "id")
        self.assertEqual(parameters[0].objc_type, "NSNumber*")
        self.assertEqual(parameters[1].name, "title")
        self.assertEqual(parameters[1].objc_type, "NSString*")

    """
    Swift Parameter Tests
    """
    def test_get_swift_data_type(self):
        array_field = Field("message", ["string", "array"])
        self.assertEqual(SwiftParameter.get_swift_data_type(array_field), "Array")

        text_field = Field("title", ["string", "optional"])
        self.assertEqual(SwiftParameter.get_swift_data_type(text_field), "String")

    def test_create_swift_id_parameter(self):
        request_object = DataObject("$postRequest", {
            "title": "string"
        })
        self.assertIsNone(SwiftParameter.create_id_parameter("/post/", request_object))
        self.assertIsNotNone(SwiftParameter.create_id_parameter("/post/:id/", request_object))

        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string"
        })
        self.assertIsNone(SwiftParameter.create_id_parameter("/post/:id/", request_object))

    def test_generate_swift_relationship_parameters(self):
        schema = create_dynamic_schema({
            "$userRequest": {
                "username": "string",
                "profile": "O2O,$profileRequest",
                "tags": "M2M,$tagRequest"
            },
            "$profileRequest": {},
            "$tagRequest": {}
        }, [])
        request_object = schema.data_objects['$userRequest']
        parameters = SwiftParameter.generate_relationship_parameters(request_object)
        self.assertEqual(parameters[0].name, "profile")
        self.assertEqual(parameters[0].swift_type, "ProfileRequest")
        self.assertEqual(parameters[1].name, "tags")
        self.assertEqual(parameters[1].swift_type, "NSOrderedSet")

    def test_generate_swift_field_parameters(self):
        request_object = DataObject("$postUpdateRequest", {
            "id": "int,primarykey",
            "title": "string",
            "tags": "M2M,$tagRequest"
        })
        parameters = SwiftParameter.generate_field_parameters(request_object)
        self.assertEqual(parameters[0].name, "id")
        self.assertEqual(parameters[0].swift_type, "Int")
        self.assertEqual(parameters[1].name, "title")
        self.assertEqual(parameters[1].swift_type, "String")
