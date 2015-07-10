import mock
import unittest
import subprocess

class SettingsTestCase(unittest.TestCase):
    def empty_string(self):
        return ""

    # @mock.patch("yak_communication.generators.ios.ios_generator.subprocess")
    @mock.patch('subprocess.check_output', side_effect=empty_string)
    def test_run_command(self, mock_subprocess):
        # mock_subprocess.check_output.return_value = ""
        command = "python -m yak_communication --schema ./tests/files/test_schema.json --generator ios " \
                  "--datamodels ./tests/files/ --coredata ./tests/files/dummycontents --projectname YetiProject"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")
        self.assertIn("Finished generating your files!", output)

'''
        # Verify successful generation using the --settingspath argument
        command = "python -m yak_communication --settingspath ./tests/files"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        #self.assertEqual(error, "")
        #self.assertIn("Finished generating your files!", output)

        # Remove the settings file
        command = "rm ./tests/files/.signalsconfig"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ensure that attempting to use the settings path fails now
        command = "python -m yak_communication --settingspath ./tests/files"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        #self.assertIn(error, "Settings file")
        #self.assertIn(error, "not found")

'''