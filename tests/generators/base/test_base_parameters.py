import unittest
from signals.generators.base.base_parameters import Parameter
from signals.generators.ios.objc.parameters import ObjCParameter
from signals.generators.ios.swift.parameters import SwiftParameter
from signals.parser.fields import Field
from signals.parser.schema import DataObject
from tests.utils import create_dynamic_schema


class ParametersTestCase(unittest.TestCase):
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
