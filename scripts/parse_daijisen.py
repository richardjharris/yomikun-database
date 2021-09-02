#!/usr/bin/env python3

# Parses JSON records generated by zero-epwing from a EPWING
# format dictionary. Returns names as JSONL.

from __future__ import annotations
import sys
import regex
import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from yomikun.models import NameType, NameData, Lifetime
from yomikun.utils.split import split_kanji_name
from yomikun.daijisen.year import parse_birth_and_death_year


def name_from_entry(heading: str, text: str) -> NameData | None:
    """
    Extract NameData from a Daijisen entry (heading and lifespan). Entries
    without a lifespan are ignored, to reduce non-person false positives.

    Daijisen splits the furigana reading into last/first name parts, but
    not the kanji, so we use a heuristic to split it. This heuristic is quite
    rough atm but should suffice; it may be improved later.

    Other things we don't handle:
     - names written with kana (the dictionary does not include any afaik)
     - の as a silent middle name, e.g.
       "ふじわら‐の‐なりちか【藤原成親】ふぢはら‐\n［一一三八〜一一七七］平安後期の公卿。"
    """
    if m := regex.match(r'^(\p{Hiragana}+)‐(\p{Hiragana}+)【(\p{Han}+)】', heading):
        sei, mei, kanji = m.groups()
        reading = NameData(kanji, f'{sei} {mei}')

        result = parse_birth_and_death_year(text)

        # Skip entries with no year information, as they are not people.
        if not result:
            return None

        reading.lifetime = Lifetime(result.birth_year, result.death_year)

        # Attempt to split the kanji into surname + first name
        reading.kaki = split_kanji_name(reading.kaki, reading.yomi)

        reading.source = f"daijisen:{heading}"
        return reading
    else:
        return None


if __name__ == '__main__':
    root = json.load(sys.stdin)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        heading = entry['heading']

        if 'text' not in entry:
            print(f"No text for entry '{heading}'", file=sys.stderr)
            continue

        text = entry['text']
        if reading := name_from_entry(heading, text):
            print(reading.to_jsonl())


def test_parse_daijisen():
    assert name_from_entry(
        "しみず‐はまおみ【清水浜臣】しみづ‐",
        "しみず‐はまおみ【清水浜臣】しみづ‐\n［一七七六〜一八二四］江戸後期の歌人・国学者。江戸の人。号、泊{{w_49708}}舎（さざなみのや）。" +
        "村田春海に国学を学び、古典の考証・注釈にすぐれ、王朝的情趣のある歌文を残した。著「泊{{w_49708}}舎文藻」「泊{{w_49708}}舎集」など。\n",
    ) == NameData(
        kaki="清水 浜臣",
        yomi="しみず はまおみ",
        lifetime=Lifetime(1776, 1824),
        source='daijisen:しみず‐はまおみ【清水浜臣】しみづ‐'
    )
