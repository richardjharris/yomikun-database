import sys

import click

import yomikun.parsers.epwing.daijisen.parser
from yomikun.parsers.epwing.parser import EpwingParser


@click.command()
def parse_daijisen():
    """
    Generate NameData from Daijisen

    Input must be the Daijisen dictionary converted to JSON format.

    Output is NameData in JSONL format.
    """
    parser = yomikun.parsers.epwing.daijisen.parser.name_from_entry
    EpwingParser(parser).parse_json_input(sys.stdin)
