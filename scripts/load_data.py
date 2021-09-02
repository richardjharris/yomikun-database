"""
Load the concatenated JSONL data produced by the various parser scripts
into an SQLite database.
"""

import sys
import json

import yomikun.loader

loader = yomikun.loader.Loader()

for line in sys.stdin:
    data = json.loads(line)
    loader.ingest(data)

loader.load()
