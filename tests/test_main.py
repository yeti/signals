import unittest
import subprocess
from signals.main import run_main
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
                     "http://test.com/api/v1/")
            self.assertEqual(error.getvalue(), "")
            self.assertIn("Finished generating your files!", out.getvalue())
