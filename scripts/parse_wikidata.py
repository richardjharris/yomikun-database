#!/usr/bin/env python3

"""
Convert queried wikidata results (from fetch_wikidata.py) into JSONL format
for dictionary loading.
"""

from __future__ import annotations
import logging
import argparse
import sys
import json
import regex

from yomikun.utils.split import split_kanji_name
from yomikun.utils.romaji import romaji_to_hiragana
from yomikun.models import NameData, Lifetime, NameAuthenticity


def extract(data: dict, path: str) -> str | None:
    parts = path.split('.')
    try:
        while parts:
            data = data[parts.pop(0)]
        assert isinstance(data, str)
        return data
    except KeyError:
        return None


def year(date: str | None):
    if date:
        if date.startswith('t'):
            # Is a bnode
            return None
        return int(date[0:4])
    else:
        return None


def gender(s: str | None):
    if s:
        if s == "男性":
            return "masc"
        elif s == "女性":
            return "fem"


# Load birth-name data, which we did in a separate query
birth_name = {}
seen = set()
for line in open('data/birth-names.jsonl').readlines():
    data = json.loads(line)
    birth_name[data['item']] = data

for line in sys.stdin:
    data: dict = json.loads(line)
    item = extract(data, 'item.value')

    if item in seen:
        # Sometimes we get duplicate records e.g. with slightly different values
        # for birth date
        continue

    seen.add(item)

    # Prefer nativeName if available, as itemLabel can contain other information
    # in brackets.

    kanji = extract(data, 'nativeName.value') or ''
    if not regex.search(r'^\p{Han}', kanji):
        # Try native name
        kanji2 = extract(data, 'itemLabel.value') or ''
        if regex.search(r'^\p{Han}', kanji2):
            kanji = kanji2
        else:
            #logging.error(f"Entry with no surname kanji: {data}")
            # TBD possibly some of these are fine, but majority are junk
            # at least reject anything with all-romaji/katakana
            continue

    kana = extract(data, 'kana.value')
    assert kana is not None

    kanji = split_kanji_name(kanji, kana)

    lifetime = Lifetime(year(extract(data, 'dob.value')),
                        year(extract(data, 'dod.value')))

    namedata = NameData(kanji, kana, lifetime=lifetime,
                        source=f'wikidata:{item}')
    tags = []
    if tag := gender(extract(data, 'genderLabel.value')):
        namedata.add_tag(tag)

    birth_name_ = birth_name.get(item, None)
    if birth_name_:
        namedata.authenticity = NameAuthenticity.PSEUDO
        # TBD add subreading
        if 'birthNameKana' in birth_name_:
            kanji, kana = birth_name_[
                'birthName'], birth_name_['birthNameKana']
            kanji = split_kanji_name(kanji, kana)
            namedata.add_subreading(NameData(kanji, kana))

    #description = extract(data, 'itemDescription')
    #country_ = extract(data, 'countryLabel.value')
    print(namedata.to_jsonl())
