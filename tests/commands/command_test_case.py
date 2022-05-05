from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path
import re
from click.testing import CliRunner
import yaml
from yomikun.scripts.yomikun import cli


@dataclass
class CommandTestCase:
    """
    Defines a CLI test case, generally parsed `from_file` in the testcases/ directory.

    The format is simply one or more blocks separated by '---' lines.
    First block defines metadata (YAML format), supporting these fields:
      command: yomikun subcommand to run, e.g. 'parse-pdd'
               may be a string or array
      exception: if set, expect an exception containing this substring
      exit_code: if set, expect this exit code (rather than 0)
      loggging:  if set (list of strings), for each string, expect an exception
                 containing the strings. If unset, ignore logs.
    Second block is input data.
    Third block is expected stdout data.
    Fourth block is expected stderr data. This may contain placeholders such as '<seconds>'
      (names are arbitrary) to pattern match against the real stderr.

    Missing blocks default to the empty string.
    """

    name: str
    command: str
    input: str
    expected_stdout: str
    expected_stderr: str
    expected_exit_code: int
    expected_exception: str | None
    expected_logging: list[str]

    @classmethod
    def from_file(cls, file: Path) -> CommandTestCase:
        with open(file, 'r') as fh:
            return cls.from_string(fh.read(), file.name)

    @classmethod
    def from_string(cls, string: str, test_name: str) -> CommandTestCase:
        parts = string.split("---\n")
        assert 1 <= len(parts) <= 4
        metadata = yaml.load(''.join(parts[0]), Loader=yaml.BaseLoader)
        input = parts[1] if len(parts) >= 2 else ''
        output = parts[2] if len(parts) >= 3 else ''
        stderr = parts[3] if len(parts) == 4 else ''
        return CommandTestCase(
            name=test_name,
            command=metadata['command'],
            input=input,
            expected_stdout=output,
            expected_stderr=stderr,
            expected_exit_code=int(metadata.get('exit_code', '0')),
            expected_exception=metadata.get('exception'),
            expected_logging=metadata.get('logging', []),
        )

    def run(self, caplog):
        runner = CliRunner(mix_stderr=False)
        logging.info(f"Command: {self.command}")

        with caplog.at_level(logging.INFO):
            result = runner.invoke(cli, self.command, input=self.input)

        logging.info(f"Got stdout: {result.stdout}")
        logging.info(f"Got stderr: {result.stderr}")

        assert result.stdout == self.expected_stdout
        assert re.match(self.expected_stderr_pattern, result.stderr)
        assert result.exit_code == self.expected_exit_code

        if self.expected_exception:
            assert self.expected_exception in str(result.exception)
        else:
            assert result.exception is None

        messages = list(caplog.messages)
        for expected_log in self.expected_logging:
            assert any(
                expected_log in m for m in messages
            ), f'Logs should contain "{expected_log}"'

    @property
    def expected_stderr_pattern(self):
        # Replace any '<token>' placeholders with '.*'
        pattern = re.escape(self.expected_stderr)
        pattern = re.sub(r'<\w+>', '.*?', pattern)
        return pattern
