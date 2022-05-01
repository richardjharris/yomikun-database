"""
Tests the parse-pdd subcommand.
"""


from tests.commands.helper import check_fixture


def test_parse_pdd():
    check_fixture('pdd', ['parse-pdd'])
