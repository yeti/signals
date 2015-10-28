import mock
import unittest
import subprocess
from signals.main import run_signals, project_specified
from tests.utils import captured_stderr, captured_stdout


class SettingsTestCase(unittest.TestCase):

    @mock.patch("signals.generators.ios.ios_generator.subprocess")
    def test_run_command(self, mock_subprocess):
        mock_subprocess.check_output.return_value = ""

        # Run normally to generate settings file
        with captured_stderr() as error, captured_stdout() as out:
            run_signals("./tests/files/test_schema.json", "objc", "./tests/files/",
                        "./tests/files/doubledummy.xcdatamodeld", True, "YetiProject", True)
            self.assertEqual(error.getvalue(), "")
            self.assertIn("Finished generating your files!", out.getvalue())

        # Verify successful generation using the --settingspath argument
        with captured_stderr() as error, captured_stdout() as out:
            project_specified(None, None, "./tests/files")
            self.assertEqual(error.getvalue(), "")
            self.assertIn("Finished generating your files!", out.getvalue())

        # Remove the settings file
        command = "rm ./tests/files/.signalsconfig"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")

        # Ensure that attempting to use the settings path fails now
        with captured_stderr() as error, captured_stdout() as out:
            project_specified(None, None, "./tests/files")
            self.assertIn("Settings file", out.getvalue())
            self.assertIn("not found", out.getvalue())
