import unittest
from flake8.engine import get_style_guide
import sys
import os

__author__ = 'nickalekhine'


class SyntaxTest(unittest.TestCase):
    def test_syntax(self):
        """
        From flake8
        """
        packages = ['signals']

        # Prepare
        config_file = os.path.join(os.path.dirname(__file__), '..', 'setup.cfg')
        flake8_style = get_style_guide(config_file=config_file)
        options = flake8_style.options

        if options.install_hook:
            from flake8.hooks import install_hook
            install_hook()

        # Save to file for later printing instead of printing now
        old_stdout = sys.stdout
        sys.stdout = out = open('.syntax_output', 'w+')

        # Run the checkers
        report = flake8_style.check_files(paths=packages)

        sys.stdout = old_stdout

        # Print the final report
        options = flake8_style.options
        if options.statistics:
            report.print_statistics()
        if options.benchmark:
            report.print_benchmark()
        if report.total_errors:
            out.close()
            with open(".syntax_output") as f:
                self.fail("{0} Syntax warnings!\n\n{1}".format(report.total_errors, f.read()))
