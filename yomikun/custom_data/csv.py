import csv
import logging
from typing import Optional, TextIO

import regex

from yomikun.models import NameData

# CSV field names
CSV_FIELDS = ('kaki', 'yomi', 'tags', 'lifetime', 'notes')

# Remember last CSV input line, for error handling
LAST_RAW_LINE = ''
LAST_RAW_LINE_NUMBER = 0


def parse_file(
    input_file: TextIO, output_file: TextIO, input_filename: Optional[str] = None
) -> bool:
    """
    Parse a CSV file and write JSONL output.

    If an error is encountered, displays contextual information and returns False.
    The caller should then exit the program.
    """
    reader = csv.DictReader(skip_lines_and_comments(input_file), CSV_FIELDS)
    for row in reader:
        namedata = None
        try:
            namedata = NameData.from_csv(row)
            namedata.source = 'custom'
            namedata.validate()
            print(namedata.to_jsonl(), file=output_file)
        except ValueError as e:
            location = f"line {LAST_RAW_LINE_NUMBER}"
            if input_filename:
                location = f"file '{input_filename}' {location}"

            logging.exception(
                f"Error parsing {location}\n"
                f"Error: {e}\n\n"
                f"Raw line: {LAST_RAW_LINE}\n"
                f"Generated dict: {row}\n"
                f"Generated namedata: {namedata}"
            )
            return False

    return True


def skip_lines_and_comments(lines):
    global LAST_RAW_LINE
    global LAST_RAW_LINE_NUMBER

    LAST_RAW_LINE_NUMBER = 0

    for line in lines:
        LAST_RAW_LINE = line.rstrip()
        LAST_RAW_LINE_NUMBER += 1
        line = regex.sub(r'#.*$', '', line)
        if regex.search(r'\S', line):
            yield line.rstrip()
