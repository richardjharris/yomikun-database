"""
Anonymise a list of [person] namedata entries by splitting them into
given name/surname pairs, which can then be sorted/shuffled.

Will skip over any records that cannot be split.
"""

import json
import logging
import sys
import os
import time

from yomikun.models.namedata import NameData

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

ok, error = 0, 0
start_time = time.monotonic()

names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)
for name in names:
    try:
        sei, mei = name.split()
        print(sei.to_jsonl())
        print(mei.to_jsonl())
        ok += 1
    except ValueError as e:
        logging.error(f"Unable to split {name}: {e}")
        error += 1

elapsed = time.monotonic() - start_time
logging.info(
    f"Processed {ok+error} records ({error} errors) in {elapsed:.0f}s")
