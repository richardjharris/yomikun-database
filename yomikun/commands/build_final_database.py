import json
import sys

import click

from yomikun.loader.finaldb import make_final_db
from yomikun.models import NameData
from yomikun.utils.timer import Timer


@click.command()
@click.argument('input', type=click.File('r'), default='-')
@click.option(
    '--genderdb',
    default='db/gender.jsonl',
    help='Path to gender score database',
)
def build_final_database(input, genderdb):
    """
    Build final.jsonl for SQLite load

    Builds final.jsonl, aggregated data suitable for loading into
    SQLite.

    Aggregate NameData on STDIN and produce output on STDOUT
    with one line per yomi/kaki/part and the total hits, split by
    gender and authenticity. Person records will be split into
    surname and given name parts.
    """
    timer = Timer()
    names = (NameData.from_dict(json.loads(line)) for line in input)
    make_final_db(names_in=names, genderdb_file_in=genderdb, db_out=sys.stdout)
    timer.report('Generated final database')
