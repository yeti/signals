import unittest
from nose.tools import eq_
from yak_communication.parser.schema import DataObject


class SchemaTestCase(unittest.TestCase):
    def test_empty_object(self):
        data_object = DataObject("$testRequest", {})
        eq_(data_object.properties(), [])
