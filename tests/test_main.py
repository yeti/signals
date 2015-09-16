import click
import mock
import unittest
import subprocess
from signals.main import run_main, add_trailing_slash_to_api, validate_schema_path
from tests.utils import captured_stderr, captured_stdout


class MainTestCase(unittest.TestCase):
    def test_run_command(self):
        command = "python -m signals --schema ./tests/files/test_schema.json --generator ios " \
                  "--datamodels ./tests/files/ --projectname YetiProject --apiurl http://test.com/api/v1/"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.assertEqual(error, "")
        self.assertIn("Finished generating your files!", output)

    def test_run_main(self):
        with captured_stderr() as error, captured_stdout() as out:
            run_main("./tests/files/test_schema.json", "ios", "./tests/files/", None, "YetiProject",
                     "http://test.com/api/v1/", False)
            self.assertEqual(error.getvalue(), "")
            self.assertIn("Finished generating your files!", out.getvalue())

    @mock.patch("signals.generators.ios.ios_generator.subprocess")
    def test_run_main_error(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "Xcode.app"
        with captured_stdout() as out:
            run_main("./tests/files/test_schema.json", "ios", "./tests/files/", "./core/data/path", "YetiProject",
                     "http://test.com/api/v1/", False)
            self.assertIn("Must quit Xcode before writing to core data", out.getvalue())

    #
    # Tests for command option callback functions:
    #
    @mock.patch('os.path')
    def test_validate_schema_path_with_full_path(self, mock_path):
        full_path = '/projects/test.json'
        mock_path.isfile.return_value = True

        validate_schema_path(None, None, full_path)

        mock_path.isfile.assert_called_with(full_path)

    @mock.patch('os.path')
    def test_validate_schema_path_with_expanduser(self, mock_path):
        no_home_dir_path = '~/test.json'
        mock_path.expanduser.return_value = '/projects/test.json'

        validate_schema_path(None, None, no_home_dir_path)

        mock_path.expanduser.assert_called_with(no_home_dir_path)
        mock_path.isfile.assert_called_with(mock_path.expanduser.return_value)

    @mock.patch('os.path')
    def test_validate_schema_path_with_abspath(self, mock_path):
        no_home_dir_path = './test.json'
        mock_path.abspath.return_value = '/projects/test.json'

        validate_schema_path(None, None, no_home_dir_path)

        mock_path.abspath.assert_called_with(no_home_dir_path)
        mock_path.isfile.assert_called_with(mock_path.abspath.return_value)

    @mock.patch('os.path')
    def test_validate_schema_path_fails(self, mock_path):
        bad_file_path = 'bad_path'
        mock_path.isfile.return_value = False

        args = {'ctx': None, 'param': None, 'value': bad_file_path}
        self.assertRaises(click.BadParameter, validate_schema_path, **args)

    def test_add_trailing_slash_to_api(self):
        url_no_slash = 'http://test.com'
        url_with_slash = add_trailing_slash_to_api(None, None, url_no_slash)
        # '/' has been added to the url string if it did not end in a slash
        self.assertEqual(url_with_slash, 'http://test.com/')

        same_url = add_trailing_slash_to_api(None, None, url_with_slash)
        # '/' has not been added to the url string if it already ended in a slash
        self.assertEqual(same_url, 'http://test.com/')

