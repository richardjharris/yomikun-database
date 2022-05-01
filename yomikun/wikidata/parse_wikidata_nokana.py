from __future__ import annotations
import logging
import json
from typing import TextIO
import regex

from yomikun.utils.split import try_to_swap_names
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy
from yomikun.models import NameData, Lifetime
from yomikun.wikidata.common import year


def parse_wikidata_nokana(input: TextIO):
    """
    Convert queried wikidata results on STDIN into NameData JSONL records.

    Compared to the Japanese WikiData pipeline (`yomikun fetch-wikidata` and
    `yomikun parse-wikidata`) this version accepts a different, simpler input
    format as I downloaded the data directly from the web UI, instead of making
    API queries. As a result it has its own parsing script. At some point
    the two ought to be unified.
    """
    seen = set()
    for line in input:
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

        kanji = kanji.replace('・', ' ')  # happens 3 times

        romaji = data['itemLabel']

        # Swap the names around
        if len(romaji.split()) != 2:
            continue

        romaji = ' '.join(reversed(romaji.split()))

        # TODO use messy parsing for now. Will re-run with improved dictionary later
        # TODO should just use the same logic as researchmap
        kana = romaji_to_hiragana_messy(romaji, kanji)

        # Since we used the 'messy' method, no dictionary was consulted so the names
        # may be in the wrong order. Try to swap if sensible.
        kanji, kana = try_to_swap_names(kanji, kana)

        if regex.search('[a-z]', kana, regex.I):
            continue

        lifetime = Lifetime(year(data.get('dob', None)), year(data.get('dod', None)))

        # Include xx-romaji tag, as we only have romaji data
        namedata = NameData(
            kanji,
            kana,
            lifetime=lifetime,
            source=f'wikidata:{item}',
            tags={'xx-romaji'},
        )

        if tag := gender_en(data.get('genderLabel', None)):
            namedata.add_tag(tag)

        namedata.add_tag('person')
        try:
            namedata.clean_and_validate()
            print(namedata.to_jsonl())
        except ValueError as e:
            logging.error(f"Validation failure: {e}")


def gender_en(s: str | None):
    if s:
        if s == "male":
            return "masc"
        elif s == "female":
            return "fem"
