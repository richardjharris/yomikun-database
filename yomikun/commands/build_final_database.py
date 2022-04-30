import json
import sys
import click
from yomikun.models import NameData
from yomikun.loader.finaldb import make_final_db
from yomikun.utils.timer import Timer


@click.command()
def build_final_database():
    """
    Build final.jsonl for SQLite load

    Builds final.jsonl, aggregated data suitable for loading into
    SQLite.

    Aggregate NameData on STDIN and produce output on STDOUT
    with one line per yomi/kaki/part and the total hits, split by
    gender and authenticity. Person records will be split into
    surname and given name parts.

    Also requires db/gender.jsonl for gender scores.
    """
    timer = Timer()
    names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)
    make_final_db(names, db_out=sys.stdout)
    timer.report('Generated final database')
