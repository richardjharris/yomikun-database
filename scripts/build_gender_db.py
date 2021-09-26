"""
Processes de-duped Person entries (from aggregate_data.py) and builds
a gender dictionary and trains a machine learning model which can be
used to guess missing gender information.
"""
import json
import sys
import logging
from yomikun.models import NameData
from yomikun.gender import make_gender_dict

logging.basicConfig(level=logging.DEBUG)

name_lists = json.load(open('data/name_lists.json'))

names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)

try:
    result = make_gender_dict(names, name_lists)
except KeyboardInterrupt:
    logging.warning('Caught SIGINT, exiting')
    pass
except:
    logging.exception('Error generating gender DB')
