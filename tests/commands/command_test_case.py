from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, TextIO

import regex
import yaml
from click.testing import CliRunner

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
    Any subsequent blocks should begin with a line: '%identifier%' (no quotes)
      These are extra input files. They can be included in the command in place of
      an actual file, e.g. 'command: build-final-database --genderdb %identifier%'

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
    other_files: dict[str, Any]

    @classmethod
    def from_file(cls, file: Path) -> CommandTestCase:
        with open(file, 'r', encoding='utf-8') as fh:
            return cls.from_handle(fh, file.name)

    @classmethod
    def from_handle(cls, handle: TextIO, test_name: str) -> CommandTestCase:
        return cls.from_string(handle.read(), test_name)

    @classmethod
    def from_string(cls, string: str, test_name: str) -> CommandTestCase:
        parts = string.split("---\n")
        metadata = yaml.load(''.join(parts[0]), Loader=yaml.BaseLoader)
        input = parts[1] if len(parts) >= 2 else ''
        output = parts[2] if len(parts) >= 3 else ''
        stderr = parts[3] if len(parts) == 4 else ''

        other_files = cls._parse_other_files(parts[4:])

        return CommandTestCase(
            name=test_name,
            command=metadata['command'],
            input=input,
            expected_stdout=output,
            expected_stderr=stderr,
            expected_exit_code=int(metadata.get('exit_code', '0')),
            expected_exception=metadata.get('exception'),
            expected_logging=metadata.get('logging', []),
            other_files=other_files,
        )

    def run(self, caplog):
        runner = CliRunner(mix_stderr=False)

        # Replace %identifier%s with filenames
        command = regex.sub(
            r'%(\w+)%', lambda m: self.other_files[m[1]].name, self.command
        )

        logging.info(f"Command: {command}")

        with caplog.at_level(logging.INFO):
            result = runner.invoke(cli, command, input=self.input)

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

    @classmethod
    def _parse_other_files(cls, blocks):
        other_files = {}
        for block in blocks:
            if m := regex.search(r'^\s*%(\w+)%\s*\n', block):
                identifier = m.group(1)
                content = block[m.end() :]  # noqa: E203
                temp = NamedTemporaryFile(mode='w')
                temp.write(content)
                temp.flush()
                other_files[identifier] = temp
            else:
                raise Exception('Invalid block, should start with %identifier%')

        return other_files
