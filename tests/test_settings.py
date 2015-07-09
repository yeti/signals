import mock
import unittest
import subprocess
from yak_communication.main import run_main
from tests.utils import captured_stderr, captured_stdout


class SettingsTestCase(unittest.TestCase):
    def test_run_command(self):

        command = "python -m yak_communication --schema ./tests/files/test_schema.json --generator ios " \
                  "--datamodels ./tests/files/ --coredata ./tests/files/dummycontents --projectname YetiProject"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")
        self.assertIn("Finished generating your files!", output)


        # Verify successful generation using the --settingspath argument
        command = "python -m yak_communication --settingspath ./tests/files"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")
        self.assertIn("Finished generating your files!", output)

        # Remove the settings file
        command = "rm ./tests/files/.signalsconfig"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ensure that attempting to use the settings path fails now
        command = "python -m yak_communication --settingspath ./tests/files"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertIn(error, "Settings file")
        self.assertIn(error, "not found")
