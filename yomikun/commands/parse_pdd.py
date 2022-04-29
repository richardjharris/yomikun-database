import json
import sys
import click
import yomikun.pdd

@click.command()
def parse_pdd():
    """
    Generate NameData from the Public Domain Dictionary

    Input must be the PDD dictionary converted to JSON format.

    Output is NameData in JSONL format.
    """
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
