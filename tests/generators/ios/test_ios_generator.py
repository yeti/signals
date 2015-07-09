import mock
import unittest
from signals.generators.ios.ios_generator import iOSGenerator
from signals.logging import SignalsError
from signals.parser.schema import Schema


class iOSGeneratorTestCase(unittest.TestCase):
    @mock.patch("signals.generators.ios.ios_generator.subprocess")
    def test_is_xcode_running(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        self.assertTrue(iOSGenerator.is_xcode_running())
        mock_subprocess.check_output.return_value = ""
        self.assertFalse(iOSGenerator.is_xcode_running())

    @mock.patch("signals.generators.ios.ios_generator.subprocess")
    def test_process_error(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        generator = iOSGenerator(Schema("./tests/files/test_schema.json"), "./tests/files/", "./core/data/path",
                                 "YetiProject", "http://test.com/api/v1/")
        with self.assertRaises(SignalsError) as e:
            generator.process()
        self.assertEqual(e.exception.msg, "Must quit Xcode before writing to core data")
