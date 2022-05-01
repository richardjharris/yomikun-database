"""
Tests the parse-myoji-yurai subcommand.
"""
from tests.commands.helper import check_fixture


def test_parse_myoji_yurai():
    check_fixture('myoji-yurai', ['parse-myoji-yurai'])
