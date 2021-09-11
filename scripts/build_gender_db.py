"""
Process JSONL files and name lists from Wikipedia, produce a mapping of
(kanji, kana) -> likelihood of name being male or female.

Should be fed the wikidata and wikipedia JSONL as input. Also reads
data/name_lists.json.
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
