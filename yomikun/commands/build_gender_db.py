import json
import sys

import click

from yomikun.gender.make import make_gender_dict
from yomikun.models import NameData

NAME_LISTS_JSON = 'data/name_lists.json'
GENDER_WEIGHTS_OUT = 'db/gender.weights'


@click.command()
def build_gender_db():
    """
    Build name gender dictionary/ML model

    Builds a gender dictionary from input name data, and train a machine
    learning model which can be used to guess missing gender information.

    Inputs:
      db/deduped.jsonl (stdin)
      data/name_lists.json (for testing)

    Output:
      db/gender.jsonl (stdout)
      db/gender.weights (ML model)
    """
    with open(NAME_LISTS_JSON, encoding='utf-8') as fh:
        name_lists = json.load(fh)

    names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)

    make_gender_dict(names, name_lists, dict_out=sys.stdout, weights=GENDER_WEIGHTS_OUT)
