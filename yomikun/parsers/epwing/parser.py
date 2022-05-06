import json
import logging
from typing import TextIO


class EpwingParser:
    def __init__(self, parser_function):
        self.name_from_entry = parser_function

    def parse_json_input(self, input: TextIO):
        """
        Parse JSON input data and output NameData as JSONL.
        """
        root = json.load(input)
        entries = root['subbooks'][0]['entries']
        for entry in entries:
            if 'heading' not in entry:
                continue

            heading = entry['heading']

            if 'text' not in entry:
                logging.warning(f"No text for entry '{heading}'")
                continue

            text = entry['text']
            if reading := self.name_from_entry(heading, text):
                print(reading.to_jsonl())
