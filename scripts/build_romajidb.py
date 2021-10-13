"""
RomajiDB is for helping convert ambiguous romaji (such as Goto Yuusuke
rather than Gotou Yuusuke) into kana using the kanji as a hint.

We take all the JSON data, except those tagged with xx-romaji (which were
themselves generated from ambiguous romaji, so we don't accidentally
create a feedback loop). Then generate a mapping of (kanji, romaji_key, mei/sei) -> (kana)

In most cases there is a clearly obvious choice, in some cases there may be
multiple viable choices, in which case we do not create an entry at all.
"""
import sys
import json
import logging
import os
import time

from yomikun.models import NameData
from yomikun.romajidb import make_romajidb

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

start_time = time.monotonic()

names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)
try:
    make_romajidb(names, db_out=sys.stdout)
except KeyboardInterrupt:
    logging.warning('Caught SIGINT, exiting')
    pass
except:
    logging.exception('Error generating romaji DB')
    sys.exit(1)

elapsed = time.monotonic() - start_time
print(f'Generated RomajiDB in {elapsed:.0f}s', file=sys.stderr)
