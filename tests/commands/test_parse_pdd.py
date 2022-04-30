"""
Tests the parse-pdd subcommand.
"""
from pathlib import Path
from click.testing import CliRunner
from yomikun.scripts.yomikun import cli

FIXTURE_DIR = Path(__file__).parent.joinpath('fixtures')


def test_parse_pdd():
    input_file = FIXTURE_DIR.joinpath('pdd-input.json')
    with open(
        FIXTURE_DIR.joinpath('pdd-expected-output.jsonl'), encoding='utf-8'
    ) as fh:
        expected_output = fh.read()

    runner = CliRunner()
    result = runner.invoke(cli, ['parse-pdd', str(input_file)])
    # assert result.exit_code == 0
    assert result.output == expected_output
