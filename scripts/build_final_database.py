"""
Builds the final database which aggregates all data, in JSONL format,
to stdout.

Requires deduped.json as input, and also uses db/gender.jsonl.
"""
import sys
import json
import logging
import os
import time

from yomikun.models import NameData
from yomikun.loader.finaldb import make_final_db

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

start_time = time.monotonic()

names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)
try:
    make_final_db(names, db_out=sys.stdout)
except KeyboardInterrupt:
    logging.warning('Caught SIGINT, exiting')
    pass
except:
    logging.exception('Error generating final DB')
    sys.exit(1)

elapsed = time.monotonic() - start_time
print(f'Generated final database in {elapsed:.0f}s', file=sys.stderr)
