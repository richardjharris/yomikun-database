"""
Tests the parse-myoji-yurai subcommand.
"""
# TODO: refactor this + pdd
from pathlib import Path
from click.testing import CliRunner
from yomikun.scripts.yomikun import cli

FIXTURE_DIR = Path(__file__).parent.joinpath('fixtures')


def test_parse_myoji_yurai():
    input_file = FIXTURE_DIR.joinpath('myoji-yurai-input.csv')
    with open(
        FIXTURE_DIR.joinpath('myoji-yurai-expected-output.jsonl'), encoding='utf-8'
    ) as fh:
        expected_output = fh.read()

    runner = CliRunner()
    result = runner.invoke(cli, ['parse-myoji-yurai', str(input_file)])
    assert result.output == expected_output
    assert result.exit_code == 0
