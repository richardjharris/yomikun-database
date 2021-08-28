#!/usr/bin/env python3

# Parses names out of Koujien

from __future__ import annotations
import sys
import regex
import json
from dataclasses import dataclass

import json_stream
from dataclasses_json import dataclass_json

from models import NameType, NameData, Lifetime
from utils.split import split_kanji_name


def name_from_entry(heading: str, text: str) -> NameData | None:
    """
    Extract NameData from a Koujien entry.
    """
    if m := regex.match(r'^(\p{Hiragana}+)‐(\p{Hiragana}+)【(\p{Han}+)】', heading):
        sei, mei, kanji = m.groups()
        reading = NameData(kanji, f'{sei} {mei}')

        lines = text.splitlines()
        if m := regex.search(r'（(\d{4})〜(\d{4})?）$', lines[1]):
            birth = int(m[1])
            death = int(m[2]) if m[2] else None
            reading.lifetime = Lifetime(birth, death)
        else:
            # Possibly not a person
            return None

        # Attempt to split the kanji into surname + first name
        reading.kaki = split_kanji_name(reading.kaki, reading.yomi)

        return reading
    else:
        return None


if __name__ == '__main__':
    root = json_stream.load(sys.stdin)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        heading = entry['heading']
        text = entry['text']
        if reading := name_from_entry(heading, text):
            print(reading.to_jsonl())


def test_parse_koujien():
    data = {
        "heading": "おぶち‐けいぞう【小渕恵三】ヲ‥ザウ",
        "text": "おぶち‐けいぞう【小渕恵三】ヲ‥ザウ\n政治家。群馬県生れ。早大卒。官房長官・外相を歴任。1998年自由民主党総裁・首相。在任中に急死。（1937〜2000）\n小渕恵三\n提供：毎日新聞社\n小渕恵三官房長官、「平成」の新元号を発表（1989年01月07日）\n提供：毎日新聞社\n{{w_46677}}おぶち【小渕】\n"
    }

    assert name_from_entry(data['heading'], data['text']) == NameData(
        kaki="小渕 恵三",
        yomi="おぶち けいぞう",
        lifetime=Lifetime(1937, 2000),
    )
