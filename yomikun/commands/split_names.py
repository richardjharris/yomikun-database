import json
import logging
import sys
import click

from yomikun.models.namedata import NameData
from yomikun.utils.timer import Timer

@click.command()
def split_names():
    """
    Anonymise full names by splitting them

    Anonymise a list of [person] namedata entries by splitting them into
    given name/surname pairs, which can then be sorted/shuffled.

    Will skip over any records that cannot be split.
    """
    ok, error = 0, 0
    timer = Timer()

    names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)
    for name in names:
        try:
            sei, mei = name.split()
            print(sei.to_jsonl())
            print(mei.to_jsonl())
            ok += 1
        except ValueError as e:
            logging.error(f"Unable to split {name}: {e}")
            error += 1

    logging.info(
        f"Processed {ok+error} records ({error} errors) in {timer.elapsed}s")
