import unittest
from signals.generators.ios.conversion import get_objc_data_type, python_to_objc_variable, sanitize_field_name, get_proper_name
from signals.parser.fields import Field


class ConversionTestCase(unittest.TestCase):
    def test_get_objc_data_type(self):
        array_field = Field("message", ["string", "array"])
        self.assertEqual(get_objc_data_type(array_field), "NSArray*")

        text_field = Field("title", ["string", "optional"])
        self.assertEqual(get_objc_data_type(text_field), "NSString*")

    def test_python_to_objc_variable(self):
        self.assertEqual(python_to_objc_variable("verbose_description"), "verboseDescription")
        self.assertEqual(python_to_objc_variable("verbose_description", capitalize_first=True), "VerboseDescription")

    def test_sanitize_field_name(self):
        self.assertEqual(sanitize_field_name("description"), "theDescription")
        self.assertEqual(sanitize_field_name("messages"), "messages")

    def test_get_proper_name(self):
        self.assertEqual(get_proper_name("unread_count"), "unreadCount")
        self.assertEqual(get_proper_name("unread_count", capitalize_first=True), "UnreadCount")
        self.assertEqual(get_proper_name("id"), "theID")
