import csv

import click

from yomikun.custom_data.csv import CSV_FIELDS
from yomikun.models.namedata import NameData


@click.command()
@click.argument('input', type=click.File('r'), default='-')
def clean_custom_data(input):
    """
    Clean up/anonymize sloppy custom.csv data

    This script converts sloppy custom.csv data, typically transcribed from
    a website or book, into standard form. It does two things:

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
    """
    reader = csv.DictReader(input, CSV_FIELDS)
    for row in reader:
        _output_clean_row(row)


def _output_clean_row(row: dict[str, str]):
    namedata = NameData.from_csv(row)

    if len(namedata.kaki.split()) != len(namedata.yomi.split()):
        raise ValueError("kaki and yomi have different name counts")

    # Split person into two parts for anonymity
    for part in namedata.extract_name_parts():
        print(part.to_csv())
