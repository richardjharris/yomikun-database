#!/usr/bin/env python3

"""
Convert queried wikidata results (from fetch_wikidata.py) into JSONL format.
This version is for data without kana, and has a slightly different (simpler)
import format because I downloaded it directly from the web UI.
"""

from __future__ import annotations
import sys
import json
import regex

from yomikun.utils.split import split_kanji_name
from yomikun.utils.romaji import romaji_to_hiragana_messy
from yomikun.models import NameData, Lifetime


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
        if s == "male":
            return "masc"
        elif s == "female":
            return "fem"


seen = set()
for line in sys.stdin:
    data: dict = json.loads(line)
    item = data['item']

    if item in seen:
        # Sometimes we get duplicate records e.g. with slightly different values
        # for birth date
        continue

    seen.add(item)

    kanji = data['nativeName']
    if not regex.search(r'^\p{Han}', kanji):
        continue

    romaji = data['itemLabel']

    # Swap the names around
    if len(romaji.split()) != 2:
        continue

    romaji = ' '.join(reversed(romaji.split()))

    # TODO use messy parsing for now. Will re-run with improved dictionary later
    kana = romaji_to_hiragana_messy(romaji, kanji)

    # Force a re-split in case the names are the wrong way around
    # TODO: could use romaji code to handle this
    old_kanji, old_kana = kanji, kana
    kanji = kanji.replace(' ', '')

    kanji = split_kanji_name(kanji, kana)

    if len(kanji.split()) == 1:
        # Try the other way around
        kana = ' '.join(reversed(kana.split()))
        kanji = split_kanji_name(kanji, kana)

        if len(kanji.split()) == 1:
            # Revert back to the original
            kanji, kana = old_kanji, old_kana

    if regex.search('[a-z]', kana, regex.I):
        continue

    lifetime = Lifetime(year(data.get('dob', None)),
                        year(data.get('dod', None)))

    # Include xx-romaji tag, as we only have romaji data
    namedata = NameData(kanji, kana, lifetime=lifetime,
                        source=f'wikidata:{item}', tags=['xx-romaji'])
    tags = []
    if tag := gender(data.get('genderLabel', None)):
        namedata.add_tag(tag)

    print(namedata.to_jsonl())
