import unittest
from signals.generators.ios.core_data import get_current_version, get_core_data_from_folder


class CoreDataTestCase(unittest.TestCase):
    def test_get_current_version(self):
        version_name = get_current_version('./tests/files/doubledummy.xcdatamodeld')
        self.assertEqual(version_name, 'dummy 2.xcdatamodel')
        version_name = get_current_version('./tests/files/dummy.xcdatamodeld')
        self.assertEqual(version_name, 'dummy.xcdatamodel')

    def test_get_core_data_from_folder(self):
        xcdatamodeld_path = './tests/files/doubledummy.xcdatamodeld'
        contents_path = xcdatamodeld_path + '/dummy 2.xcdatamodel/contents'
        self.assertEqual(get_core_data_from_folder(xcdatamodeld_path), contents_path)

        xcdatamodeld_path = './tests/files/dummy.xcdatamodeld'
        contents_path = xcdatamodeld_path + '/dummy.xcdatamodel/contents'
        self.assertEqual(get_core_data_from_folder(xcdatamodeld_path), contents_path)
