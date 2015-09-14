import mock
import unittest
import subprocess
from signals.main import run_main, add_trailing_slash_to_api
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

    def test_add_trailing_slash_to_api(self):
        url_no_slash = 'http://test.com'
        url_with_slash = add_trailing_slash_to_api(None, None, url_no_slash)
        # '/' has been added to the url string if it did not end in a slash
        self.assertEqual(url_with_slash, 'http://test.com/')

        same_url = add_trailing_slash_to_api(None, None, url_with_slash)
        # '/' has not been added to the url string if it already ended in a slash
        self.assertEqual(same_url, 'http://test.com/')
