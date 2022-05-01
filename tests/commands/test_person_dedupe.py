"""
Tests the person-dedupe subcommand using Akira Kurosawa data, and one
non-person record which should be output as-is.
"""


from tests.commands.helper import check_fixture


def test_parse_wikidata():
    check_fixture('person-dedupe', ['person-dedupe'])
