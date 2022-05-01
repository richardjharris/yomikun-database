"""
Tests the import-researchmap subcommand using a mix of valid and
invalid records.
"""


from tests.commands.helper import check_fixture


def test_import_researchmap():
    check_fixture('import-researchmap', ['--loglevel=CRITICAL', 'import-researchmap'])
