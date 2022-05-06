import sys

import click

import yomikun.parsers.epwing.koujien
from yomikun.parsers.epwing.parser import EpwingParser


@click.command()
def parse_koujien():
    """
    Generate NameData from Koujien

    Input must be the Koujien dictionary converted to JSON format.

    Output is NameData in JSONL format.
    """
    parser = yomikun.parsers.epwing.koujien.name_from_entry
    EpwingParser(parser).parse_json_input(sys.stdin)
