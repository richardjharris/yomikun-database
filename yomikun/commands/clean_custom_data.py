import csv

import click

from yomikun.custom_data.csv import CSV_FIELDS
from yomikun.models.namedata import NameData


@click.command()
@click.argument('input', type=click.File('r'), default='-')
@click.option(
    '--split/--no-split',
    type=bool,
    default=True,
    help='Split person into two name records for anonymity',
)
@click.option(
    '--swap-romaji/--no-swap-romaji',
    type=bool,
    default=True,
    help='Swap order of romaji names',
)
def clean_custom_data(input, split, swap_romaji):
    """
    Clean up/anonymize sloppy custom.csv data

    This script converts sloppy custom.csv data, typically transcribed from
    a website or book, into standard form. It does up to two things:

    \b
    1) Convert romaji/katakana names into hiragana
    2) Split full names into given and surname components

    For romaji conversion, long vowels must be spelled in full, and name order
    is Western (first name then last name).

    By sorting the split components, the original names are effectively
    anonymised.

    Example of allowed inputs:

    \b
    八久保　竜司,ハチクボ　リュウジ
    佐藤 直哉,さとう　なおや,m
    頴川 文彦,Fumihiko Egawa,m+fictional

    Limitations:
     - notes field cannot contain commas
     - some tags are not supported (stick to m,f,s)
    """
    reader = csv.DictReader(input, CSV_FIELDS)
    for row in reader:
        _output_clean_row(row, split, swap_romaji)


def _output_clean_row(row: dict[str, str], do_split: bool, swap_romaji: bool):
    namedata = NameData.from_csv(row, swap_romaji)

    if len(namedata.kaki.split()) != len(namedata.yomi.split()):
        raise ValueError(f"kaki and yomi have different name counts: {row}")

    if do_split:
        # Split person into two parts for anonymity
        for part in namedata.extract_name_parts():
            print(part.to_csv())
    else:
        print(namedata.to_csv())
