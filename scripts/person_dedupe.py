"""
Accepts JSONL input, filters people records and de-duplicates them
(based on birth_year, kaki and yomi). Resolves missing or conflicting
data for gender, authenticity, etc.

 - adds the 'person' tag to all output records
 - passes through non-person records as-is
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
in_records, out_records, passthru_records = 0, 0, 0

for line in sys.stdin:
    data = NameData.from_jsonl(line)
    if dedupe.ingest(data):
        in_records += 1
    else:
        # Print out directly
        print(line, end='')
        passthru_records += 1

for person in dedupe.deduped_people():
    try:
        person.add_tag('person')

        print(person.to_jsonl())
        out_records += 1
    except TypeError as e:
        logging.exception(person)

print(f"De-duped {in_records} input records to {out_records} output records",
      file=sys.stderr)
print(f"Passed through {passthru_records} input records", file=sys.stderr)
