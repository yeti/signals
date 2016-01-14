import unittest
from signals.generators.ios.conversion import ObjectiveCConverter


format_name = ObjectiveCConverter.format_name
sanitize_field_name = ObjectiveCConverter.sanitize_field_name
get_proper_name = ObjectiveCConverter.get_proper_name

class ConversionTestCase(unittest.TestCase):
    
    def format_name(self):
        self.assertEqual(format_name("verbose_description"), "verboseDescription")
        self.assertEqual(format_name("verbose_description", capitalize_first=True), "VerboseDescription")

    def test_sanitize_field_name(self):
        self.assertEqual(sanitize_field_name("description"), "theDescription")
        self.assertEqual(sanitize_field_name("messages"), "messages")

    def test_get_proper_name(self):
        self.assertEqual(get_proper_name("unread_count"), "unreadCount")
        self.assertEqual(get_proper_name("unread_count", capitalize_first=True), "UnreadCount")
        self.assertEqual(get_proper_name("id"), "theID")
