"""
Tests the parse-pdd subcommand.
"""
import os
from click.testing import CliRunner

from yomikun.scripts.yomikun import cli

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'fixtures',
)


def test_parse_pdd():
    input_file = FIXTURE_DIR + "/pdd-input.json"
    with open(FIXTURE_DIR + "/pdd-expected-output.jsonl", encoding='utf-8') as fh:
        expected_output = fh.read()

    runner = CliRunner()
    result = runner.invoke(cli, ['parse-pdd', input_file])
    assert result.exit_code == 0
    assert result.output == expected_output
