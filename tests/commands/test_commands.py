"""
Tests CLI commands using test cases in the testcases/ directory.

Each test case contains a command name, arguments, input, expected
output and expected standard error. As the standard error may
contain unstable data such as elapsed time, placeholders are supported.
"""
from operator import attrgetter
from pathlib import Path

from .command_test_case import CommandTestCase

TESTCASE_DIR = Path(__file__).parent.joinpath('testcases')


def pytest_generate_tests(metafunc):
    if 'test_case' in metafunc.fixturenames:
        files = TESTCASE_DIR.iterdir()
        test_cases = map(CommandTestCase.from_file, files)
        metafunc.parametrize('test_case', test_cases, ids=attrgetter('name'))


def test_commands(caplog, test_case: CommandTestCase):
    test_case.run(caplog)
