import unittest
from tests.utils import captured_stdout
from signals.parser.fields import Relationship, Field
from signals.logging import SignalsError, colorize_string


class FieldsTestCase(unittest.TestCase):
    def test_create_field(self):
        primary_field = Field("id", ["int", "primarykey"])
        self.assertTrue(primary_field.primary_key)
        self.assertEqual(primary_field.name, "id")
        self.assertEqual(primary_field.field_type, Field.INTEGER)
        self.assertFalse(primary_field.array)
        self.assertFalse(primary_field.optional)

        array_optional_field = Field("notes", ["string", "optional", "array"])
        self.assertTrue(array_optional_field.array)
        self.assertTrue(array_optional_field.optional)

    def test_field_process_attribute_error(self):
        with captured_stdout() as out:
            Field("username", ["string", "option"])
            self.assertEqual(out.getvalue().rstrip("\n"),
                             colorize_string("yellow", "Found an unexpected attribute: option on username."))

    def test_field_process_attribute_error_relationship(self):
        with self.assertRaises(SignalsError) as e:
            Field("message", ["int", "$messageResponse"])
        self.assertEqual(e.exception.msg, "Found an unexpected attribute: $messageResponse on message. "
                                          "Likely it's missing relationship type.")

    def test_field_validate_field(self):
        with self.assertRaises(SignalsError) as e:
            Field("follow", ["optional"])
        self.assertEqual(e.exception.msg, "Didn't find field type for follow, exiting.")

    def test_create_relationship(self):
        relationship = Relationship("purchases", ["M2O", "$purchaseResponse", "optional"])
        self.assertEqual(relationship.related_object, "$purchaseResponse")
        self.assertEqual(relationship.relationship_type, Relationship.MANY_TO_ONE)

    def test_relationship_validate_field(self):
        with self.assertRaises(SignalsError) as e:
            Relationship("purchases", ["M2O"])
        self.assertEqual(e.exception.msg, "Didn't find related object for purchases, exiting.")

    def test_is_relationship(self):
        self.assertTrue(Relationship.is_relationship(["O2M", "$messageResponse"]))
        self.assertFalse(Relationship.is_relationship(["email", "string"]))
