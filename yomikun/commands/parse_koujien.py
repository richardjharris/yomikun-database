import json
import sys
import click
import yomikun.koujien

@click.command()
def parse_koujien():
    """
    Generate NameData from Koujien

    Input must be the Koujien dictionary converted to JSON format.

    Output is NameData in JSONL format.
    """
    root = json.load(sys.stdin)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        heading = entry['heading']
        text = entry['text']
        if reading := yomikun.koujien.name_from_entry(heading, text):
            print(reading.to_jsonl())
