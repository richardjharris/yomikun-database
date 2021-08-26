#!/usr/bin/env python3

# Parses PDD (public domain dictionary) 人名辞典.

from __future__ import annotations
import sys
import regex
import json
from dataclasses import dataclass

import json_stream
from dataclasses_json import dataclass_json

from models import Reading, NameType, NameData


def name_from_entry(heading: str, text: str) -> NameData | None:
    """
    Heading format: "いのうえ　ああ【井上　唖々】"
    Text format: (as above) + \n + 1878. 1.30(明治11) 〜 1923. 7.11(大正12)
      Some useful text is included too.
      Start date is often 生年不詳 but the tilde always separates them.

      Sometimes header contains a second form of the name
      梅原　竜三郎(梅原　龍三郎)
      or a generation
      [1]うめわか　みのる【梅若　実(初世)】
      [2]うめわか　みのる【梅若　実(二世)】
      さんゆうてい　えんしょう【三遊亭　円生(６代)】

      A few lack spaces
      みなもとのたかあきら【源　高明】
    """
    if m := regex.match(r'^(?:\[\d+\])?(\p{Hiragana}+　\p{Hiragana}+)【(\p{Han}+　\p{Han}+)\(.*?\)】', heading):
        yomi, kaki = m.groups()
        reading = NameData(kaki, yomi)

        left, right = text.splitlines()[1].split('〜')
        if m := regex.match(r'(\d{4})\.', left):
            reading.lifetime.birth_year = m[1]
        if m := regex.match(r'(\d{4})\.', right):
            reading.lifetime.death_year = m[1]
        return reading
    else:
        raise Exception(f"Cannot parse heading {heading}")


root = json_stream.load(sys.stdin)
entries = root['subbooks'][0]['entries']
for entry in entries:
    heading = entry['heading']

    if 'text' not in entry:
        print(f"No text for entry '{heading}'", file=sys.stderr)
        continue

    text = entry['text']
    if reading := name_from_entry(heading, text):
        print(reading.to_jsonl())
