import json
from typing import TextIO
import click

import yomikun.pdd


@click.command()
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
def parse_pdd(input: TextIO, output: TextIO):
    """
    Generate NameData from the Public Domain Dictionary

    Input must be the PDD dictionary converted to JSON format.
    Defaults to stdin.

    Output is NameData in JSONL format. Defaults to stdout.

    \b
    Example:
    zcat data/pdd.jsonl.gz | yomikun parse-pdd > jsonl/pdd.jsonl
    """
    root = json.load(input)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        if 'heading' not in entry:
            continue

        heading = entry['heading']

        if 'text' not in entry:
            click.echo(f"No text for entry '{heading}'", err=True)
            continue

        text = entry['text']
        if reading := yomikun.pdd.name_from_entry(heading, text):
            print(reading.to_jsonl(), file=output)
