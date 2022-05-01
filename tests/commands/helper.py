"""
Helper method to test command line tools.
"""
from pathlib import Path
from click.testing import CliRunner
from yomikun.scripts.yomikun import cli

FIXTURE_DIR = Path(__file__).parent.joinpath('fixtures')


def check_fixture(fixture_prefix: str, command: list[str]):
    input_file = FIXTURE_DIR.joinpath(f'{fixture_prefix}-input')
    with open(
        FIXTURE_DIR.joinpath(f'{fixture_prefix}-expected-output'),
        encoding='utf-8',
    ) as fh:
        expected_output = fh.read()

    runner = CliRunner()
    result = runner.invoke(cli, [*command, str(input_file)])
    assert result.output == expected_output
    assert result.exit_code == 0
