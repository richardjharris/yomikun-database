from typing import TextIO

import click

import yomikun.parsers.epwing.pdd
from yomikun.parsers.epwing.parser import EpwingParser


@click.command()
@click.argument('input', type=click.File('r'), default='-')
def parse_pdd(input: TextIO):
    """
    Generate NameData from the Public Domain Dictionary

    Input must be the PDD dictionary converted to JSON format.
    Defaults to stdin.

    Output is NameData in JSONL format to stdout.

    \b
    Example:
    zcat data/pdd.jsonl.gz | yomikun parse-pdd > jsonl/pdd.jsonl
    """
    parser = yomikun.parsers.epwing.pdd.name_from_entry

    return EpwingParser(parser).parse_json_input(input)
