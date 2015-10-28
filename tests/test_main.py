import os
import click
import mock
import unittest
import subprocess
from signals.main import run_signals, validate_path
from signals.generators.base.base_generator import BaseGenerator
from tests.utils import captured_stderr, captured_stdout


class MainTestCase(unittest.TestCase):
    def test_run_command(self):
        command = "python -m signals --schema ./tests/files/test_schema.json --generator objc " \
                  "--datamodels ./tests/files/ --projectname YetiProject"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")
        self.assertIn("Finished generating your files!", output)

    def test_run_signals(self):
        with captured_stderr() as error, captured_stdout() as out:
            run_signals("./tests/files/test_schema.json", "objc", "./tests/files/",
                        None, False, "YetiProject", False)
            self.assertEqual(error.getvalue(), "")
            self.assertIn("Finished generating your files!", out.getvalue())

    @mock.patch("signals.generators.ios.ios_generator.subprocess")
    def test_run_signals_error(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        with captured_stdout() as out:
            run_signals("./tests/files/test_schema.json", "objc", "./tests/files/",
                        "./core/data/path", True, "YetiProject", False)
            self.assertIn("Must quit Xcode before writing to core data", out.getvalue())

    def test_clear_generated_code_files(self):
        # Currently, a previous test is creating, but not deleting, this directory.
        # Potentially could change in future, thus the check if BUILD_DIR exists.
        if not os.path.exists(BaseGenerator.BUILD_DIR):
            os.makedirs(BaseGenerator.BUILD_DIR)

        self.assertTrue(os.path.isdir(BaseGenerator.BUILD_DIR))
        BaseGenerator.clear_generated_code_files()
        self.assertFalse(os.path.isdir(BaseGenerator.BUILD_DIR))

    #
    # Tests for command option callback functions:
    #
    @mock.patch('os.path')
    def test_validate_schema_path_with_full_path(self, mock_path):
        full_path = '/projects/test.json'
        mock_path.isfile.return_value = True

        validate_path(None, None, full_path)

        mock_path.isfile.assert_called_with(full_path)

    @mock.patch('os.path')
    def test_validate_schema_path_with_expanduser(self, mock_path):
        no_home_dir_path = '~/test.json'
        mock_path.expanduser.return_value = '/projects/test.json'

        validate_path(None, None, no_home_dir_path)

        mock_path.expanduser.assert_called_with(no_home_dir_path)
        mock_path.isfile.assert_called_with(mock_path.expanduser.return_value)

    @mock.patch('os.path')
    def test_validate_schema_path_with_abspath(self, mock_path):
        no_home_dir_path = './test.json'
        mock_path.abspath.return_value = '/projects/test.json'

        validate_path(None, None, no_home_dir_path)

        mock_path.abspath.assert_called_with(no_home_dir_path)
        mock_path.isfile.assert_called_with(mock_path.abspath.return_value)

    @mock.patch('os.path')
    def test_validate_schema_path_fails(self, mock_path):
        bad_file_path = 'bad_path'
        mock_path.isfile.return_value = False
        mock_path.exists.return_value = False

        args = {'ctx': None, 'param': None, 'value': bad_file_path}
        self.assertRaises(click.BadParameter, validate_path, **args)
