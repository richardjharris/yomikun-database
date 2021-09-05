import json
import sys

import yomikun.pdd

root = json.load(sys.stdin)
entries = root['subbooks'][0]['entries']
for entry in entries:
    if 'heading' not in entry:
        continue

    heading = entry['heading']

    if 'text' not in entry:
        print(f"No text for entry '{heading}'", file=sys.stderr)
        continue

    text = entry['text']
    if reading := yomikun.pdd.name_from_entry(heading, text):
        print(reading.to_jsonl())
