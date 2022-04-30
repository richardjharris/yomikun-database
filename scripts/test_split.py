"""
Tests the split methods against input data. Usage:

cat jsonl/wikipedia_ja.jsonl | pytest scripts/test_split.py -s
"""
import sys

from yomikun.models.namedata import NameData
from yomikun.utils.split import find_split_point, find_kana_split_point

for line in sys.stdin:
    namedata = NameData.from_jsonl(line)
    try:
        sei_yomi, mei_yomi = namedata.yomi.split(' ')
        sei_kaki, mei_kaki = namedata.kaki.split(' ')
    except IndexError:
        continue

    try:
        kaki_split = find_split_point(sei_yomi, mei_yomi, f"{sei_kaki}{mei_kaki}")
        assert kaki_split == len(sei_kaki), 'kanji'

        yomi_split = find_kana_split_point(sei_kaki, mei_kaki, f"{sei_yomi}{mei_yomi}")
        assert yomi_split == len(sei_yomi), 'kana'
    except AssertionError as e:
        print('Assertion failed: ', e, "\n", line)
        # sys.exit(1)
