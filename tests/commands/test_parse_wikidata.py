"""
Tests the parse-wikidata subcommand.
"""


from tests.commands.helper import check_fixture


def test_parse_wikidata():
    check_fixture('parse-wikidata', ['parse-wikidata'])
