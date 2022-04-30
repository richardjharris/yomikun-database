import csv
import sys
import click

from yomikun.custom_data.importer import convert_to_hiragana
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData

fields = ('kaki', 'yomi', 'tags', 'lifetime', 'notes')


@click.command()
def clean_custom_data():
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

    Example of alloweed inputs:

    \b
    八久保　竜司,ハチクボ　リュウジ
    佐藤 直哉,さとう　なおや,m
    頴川 文彦,Fumihiko Egawa,m+fictional
    """
    reader = csv.DictReader(sys.stdin, fields)
    for row in reader:
        _output_clean_row(row)


def _output_clean_row(row: dict[str, str]):
    kaki = row['kaki']
    yomi = convert_to_hiragana(row['yomi'])

    if len(kaki.split()) != len(yomi.split()):
        raise ValueError("kaki and yomi have different name counts")

    namedata = NameData(kaki, yomi)

    # TODO write NameData.from_csv, else this can get out of sync if new fields are added
    if row['tags']:
        tags = row['tags'].split('+')
        for tag in tags:
            # TODO: code duplicated with parse_custom_data
            if tag == 'm':
                namedata.set_gender('masc')
            elif tag == 'f':
                namedata.set_gender('fem')
            elif tag == 's':
                namedata.add_tag('surname')
            elif tag == 'pseudo':
                namedata.authenticity = NameAuthenticity.PSEUDO
            elif tag == 'fictional':
                namedata.authenticity = NameAuthenticity.FICTIONAL
            else:
                namedata.add_tag(tag)

    if row['lifetime']:
        years = row['lifetime'].split('-')
        if len(years) > 0 and years[0]:
            namedata.lifetime.birth_year = int(years[0])
        if len(years) > 1 and years[1]:
            namedata.lifetime.death_year = int(years[1])

    if row['notes']:
        namedata.notes = row['notes']

    namedata.source = 'custom'

    # Split person into two parts for anonymity
    if namedata.is_person():
        for part in namedata.split():
            print(part.to_csv())
    else:
        print(namedata.to_csv())
