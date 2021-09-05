import json
import sys

import yomikun.daijisen.parser

root = json.load(sys.stdin)
entries = root['subbooks'][0]['entries']
for entry in entries:
    heading = entry['heading']

    if 'text' not in entry:
        print(f"No text for entry '{heading}'", file=sys.stderr)
        continue

    text = entry['text']
    if reading := yomikun.daijisen.parser.name_from_entry(heading, text):
        print(reading.to_jsonl())
