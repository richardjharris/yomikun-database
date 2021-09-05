import json
import sys

import yomikun.koujien

root = json.load(sys.stdin)
entries = root['subbooks'][0]['entries']
for entry in entries:
    heading = entry['heading']
    text = entry['text']
    if reading := yomikun.koujien.name_from_entry(heading, text):
        print(reading.to_jsonl())
