#!/usr/bin/env python

import click

from tests.commands.command_test_case import CommandTestCase


@click.command()
@click.option(
    '--section',
    type=click.Choice(['input', 'output']),
    help='Section to extract',
    default='input',
)
@click.argument('testcase', type=click.File('r'), default='-')
def get_test_data(section, testcase):
    """
    Extracts a section of test data from a test case file.
    """
    testcase_object = CommandTestCase.from_handle(testcase, testcase.name)
    match section:
        case 'input':
            print(testcase_object.input.rstrip())
        case 'output':
            print(testcase_object.expected_stdout.rstrip())


if __name__ == '__main__':
    get_test_data()
