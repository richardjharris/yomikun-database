from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
from click.testing import CliRunner
import yaml
from yomikun.scripts.yomikun import cli


@dataclass
class CommandTestCase:
    """
    Defines a CLI test case, generally parsed `from_file` in the testcases/ directory.

    The format is simply three or more blocks separated by '---' lines.
    First block defines metadata (YAML format), supporting these fields:
      command - yomikun subcommand to run, e.g. 'parse-pdd'
    Second block is input data.
    Third block is expected stdout data.
    Fourth block is expected stderr data. This may contain placeholders such as '<seconds>'
      (names are arbitrary) to pattern match against the real stderr.
      If this block is missing, it defaults to empty.
    """

    name: str
    command: str
    input: str
    expected_stdout: str
    expected_stderr: str
    expected_exit_code: int

    @classmethod
    def from_file(cls, file: Path) -> CommandTestCase:
        with open(file, 'r') as fh:
            return cls.from_string(fh.read(), file.name)

    @classmethod
    def from_string(cls, string: str, test_name: str) -> CommandTestCase:
        parts = string.split("---\n")
        assert 3 <= len(parts) <= 4
        metadata = yaml.load(''.join(parts[0]), Loader=yaml.BaseLoader)
        input = parts[1]
        output = parts[2]
        stderr = parts[3] if len(parts) == 4 else ''
        return CommandTestCase(
            name=test_name,
            command=metadata['command'],
            input=input,
            expected_stdout=output,
            expected_stderr=stderr,
            expected_exit_code=metadata.get('exit_code', 0),
        )

    def run(self):
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli, self.command, input=self.input)

        assert result.stdout == self.expected_stdout
        assert re.match(self.expected_stderr_pattern, result.stderr)
        assert result.exit_code == self.expected_exit_code

    @property
    def expected_stderr_pattern(self):
        # Replace any '<token>' placeholders with '.*'
        pattern = re.escape(self.expected_stderr)
        pattern = re.sub(r'<\w+>', '.*?', pattern)
        return pattern
