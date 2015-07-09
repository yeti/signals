import mock
import unittest
from yak_communication.generators.ios.ios_generator import iOSGenerator
from yak_communication.logging import SignalsError
from yak_communication.parser.schema import Schema
from tests.utils import captured_stdout


class iOSGeneratorTestCase(unittest.TestCase):
    @mock.patch("yak_communication.generators.ios.ios_generator.subprocess")
    def test_is_xcode_running(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        self.assertTrue(iOSGenerator.is_xcode_running())
        mock_subprocess.check_output.return_value = ""
        self.assertFalse(iOSGenerator.is_xcode_running())

    @mock.patch("yak_communication.generators.ios.ios_generator.subprocess")
    def test_process_error(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        generator = iOSGenerator(Schema("./tests/files/test_schema.json"), "./tests/files/", "./core/data/path", "YetiProject")
        with captured_stdout() as out:
            with self.assertRaises(SignalsError):
                generator.process()
                self.assertEqual(out.getValue(), "M\033[91must quit XCode before writing to core data\033[0m")