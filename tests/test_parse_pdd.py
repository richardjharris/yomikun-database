"""
Tests the parse-pdd subcommand.
"""
from click.testing import CliRunner

from yomikun.scripts.yomikun import cli


def test_parse_pdd():
    input_file = 'tests/fixtures/pdd-input.json'
    expected_output = open('tests/fixtures/pdd-expected-output.jsonl').read()

    runner = CliRunner()
    result = runner.invoke(cli, ['parse-pdd', input_file])
    assert result.exit_code == 0
    assert result.output == expected_output
