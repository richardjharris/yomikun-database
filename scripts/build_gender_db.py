"""
Processes de-duped Person entries (from person_dedupe.py) and builds
a gender dictionary and trains a machine learning model which can be
used to guess missing gender information.

Usage: cat people.json | python build_gender_db.py > output.dict.json
  # extra input: data/name_lists.json
  # extra output: db/gender.weights
"""
import json
import sys
import logging
from yomikun.models import NameData
from yomikun.gender import make_gender_dict

NAME_LISTS_JSON = 'data/name_lists.json'
GENDER_WEIGHTS_OUT = 'db/gender.weights'

logging.basicConfig(level=logging.DEBUG)

name_lists = json.load(open(NAME_LISTS_JSON))

names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)

try:
    make_gender_dict(names, name_lists, dict_out=sys.stdout,
                     weights=GENDER_WEIGHTS_OUT)
except KeyboardInterrupt:
    logging.warning('Caught SIGINT, exiting')
    pass
except:
    logging.exception('Error generating gender DB')
