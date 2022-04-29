import logging
import sys
import click

from yomikun.models import NameData
from yomikun.loader.person_dedupe import PersonDedupe

@click.command()
def person_dedupe():
    """
    De-deduplicates person records

    Accepts JSONL input, filters people records and de-duplicates them
    (based on birth_year, kaki and yomi). Resolves missing or conflicting
    data for gender, authenticity, etc.

    \b
     - adds the 'person' tag to all output records
     - passes through non-person records as-is
    """
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

    click.echo(f"De-duped {in_records} input records to {out_records} output records",
        err=True)
    click.echo(f"Passed through {passthru_records} input records", err=True)
