#!/usr/bin/env python3

# Parses PDD (public domain dictionary) 人名辞典.

from __future__ import annotations
import sys
import regex
import json


from yomikun.models import Reading, NameAuthenticity, NameData, Lifetime
from yomikun.utils.patterns import name_pat, reading_pat


def name_from_entry(heading: str, text: str) -> NameData | None:
    """
    Extract NameData from a PDD (public domain dictionary) name database entry.

    Heading format: "いのうえ　ああ【井上　唖々】"
    Text format: (as above) + \n + 1878. 1.30(明治11) 〜 1923. 7.11(大正12)

    We currently ignore the (useful) text that follows the birth/death dates.

    * Start date is often 生年不詳 but the tilde always separates them.

    * Sometimes header contains a second form of the name:
      梅原　竜三郎(梅原　龍三郎)
      or a generation:
      [1]うめわか　みのる【梅若　実(初世)】
      [2]うめわか　みのる【梅若　実(二世)】
      さんゆうてい　えんしょう【三遊亭　円生(６代)】

      A few lack spaces:
      みなもとのたかあきら【源　高明】

    TODO handle の
    TODO handle alternate form of name
    """
    if m := regex.match(fr'^(?:\[\d+\])?({reading_pat})【({name_pat})(?:\(.*?\))?】', heading):
        yomi, kaki = m.groups()
        reading = NameData(kaki, yomi)
        lines = text.splitlines()

        if len(lines) < 2:
            return

        result = text.splitlines()[1].split('〜')
        if len(result) == 2:
            left, right = result
            if m := regex.match(r'(\d{4})\.', left):
                reading.lifetime.birth_year = int(m[1])
            if m := regex.match(r'\s*(\d{4})\.', right):
                reading.lifetime.death_year = int(m[1])
        return reading
    else:
        #raise Exception(f"Cannot parse heading {heading}")
        pass


if __name__ == '__main__':
    root = json.load(sys.stdin)
    entries = root['subbooks'][0]['entries']
    for entry in entries:
        if 'heading' not in entry:
            continue

        heading = entry['heading']

        if 'text' not in entry:
            print(f"No text for entry '{heading}'", file=sys.stderr)
            continue

        text = entry['text']
        if reading := name_from_entry(heading, text):
            print(reading.to_jsonl())


def test_parse_pdd():
    assert name_from_entry(
        "さんゆうてい　えんしょう【三遊亭　円生(６代)】",
        "いのうえ　ああ【井上　唖々】\n1878. 1.30(明治11) 〜 1923. 7.11(大正12)\n◇小説家・俳人。本名は精一、別号は九穂(キュウスイ)・玉山。名古屋生れ。\n",
    ) == NameData(
        kaki="三遊亭 円生",
        yomi="さんゆうてい えんしょう",
        lifetime=Lifetime(1878, 1923),
    )
