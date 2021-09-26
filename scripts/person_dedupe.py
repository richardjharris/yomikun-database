"""
Accepts JSONL input, filters to people records and de-duplicates them
(based on birth_year, kaki and yomi). Resolves missing or conflicting
data for gender, authenticity, etc.

 - adds the 'person' tag to all output records
---

"""
import sys
import logging
import os

from yomikun.models import NameData
from yomikun.loader.person_dedupe import PersonDedupe

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

dedupe = PersonDedupe()
in_records, out_records = 0, 0

for line in sys.stdin:
    data = NameData.from_jsonl(line)
    dedupe.ingest(data)
    in_records += 1

for person in dedupe.deduped_people():
    try:
        print(person.to_jsonl())
        out_records += 1
    except TypeError as e:
        logging.exception(person)

print(f"De-duped {in_records} input records to {out_records} output records",
      file=sys.stderr)
