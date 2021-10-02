"""
Tests the split methods against input data. Usage:

cat jsonl/wikipedia_ja.jsonl | pytest scripts/test_split.py -s
"""
import sys

from yomikun.models.namedata import NameData
from yomikun.utils.split import *

for line in sys.stdin:
    namedata = NameData.from_jsonl(line)
    try:
        sei_yomi, mei_yomi = namedata.yomi.split(' ')
        sei_kaki, mei_kaki = namedata.kaki.split(' ')
    except IndexError:
        continue

    try:
        assert find_split_point(
            sei_yomi, mei_yomi, f"{sei_kaki}{mei_kaki}") == len(sei_kaki), 'kanji'
        assert find_kana_split_point(
            sei_kaki, mei_kaki, f"{sei_yomi}{mei_yomi}") == len(sei_yomi), 'kana'
    except AssertionError as e:
        print('Assertion failed: ', e)
        print()
        print(line)
        # sys.exit(1)
