from typing import TextIO

import click

from yomikun.models import NameData
from yomikun.models.name_position import NamePosition


@click.command()
@click.argument('input', type=click.File('r'), default='-')
def parse_myoji_yurai(input: TextIO):
    """
    Parse MyojiYurai reading data

    Parses myoji-yurai-readings.csv data (INPUT) to get the top 5000
    Japanese surnames and their 'typical' readings. Outputs NameData in
    JSONL format.
    """
    for line in input:
        line = line.rstrip()
        # population = e.g. 1894000 for 佐藤
        # difficulty = ranging from 0.5ish (easy) to 1000+, although it is
        #              pretty unreliable for long names
        kanji, readings_joined, population, _difficulty = line.split(',')
        readings = readings_joined.split('|')

        for reading in filter(len, readings):
            data = NameData(kanji, reading, is_dict=True, position=NamePosition.sei)
            data.source = "myoji-yurai-5000"
            data.notes = f"population:{population}"
            data.clean_and_validate()
            print(data.to_jsonl())
