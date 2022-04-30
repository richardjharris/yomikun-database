import json
import sys
import click
import yomikun.daijisen.parser


@click.command()
def parse_daijisen():
    """
    Generate NameData from Daijisen

    Input must be the Daijisen dictionary converted to JSON format.

    Output is NameData in JSONL format.
    """
    root = json.load(sys.stdin)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        heading = entry['heading']

        if 'text' not in entry:
            print(f"No text for entry '{heading}'", file=sys.stderr)
            continue

        text = entry['text']
        if reading := yomikun.daijisen.parser.name_from_entry(heading, text):
            print(reading.to_jsonl())
