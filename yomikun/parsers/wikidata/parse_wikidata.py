import json
import logging
from typing import TextIO, cast

import jcconv3
import regex

from yomikun.models import Lifetime, NameAuthenticity, NameData
from yomikun.models.gender import Gender
from yomikun.parsers.wikidata.common import extract, year
from yomikun.utils.split import split_kanji_name


def load_birth_name_data(handle: TextIO) -> dict[str, dict[str, str]]:
    birth_name = {}
    for line in handle:
        data = json.loads(line)
        birth_name[data['item']] = data
    return birth_name


def parse_wikidata(input: TextIO, birth_name_input: TextIO):
    """
    Convert queried wikidata results (from `yomikun fetch-wikidata`) into
    JSONL format for dictionary loading (on stdout).

    `birth_name_input` should be a handle to a JSON file containing
    birth name information.
    """
    # Load birth-name data, which we did in a separate query
    seen = set()
    birth_name = load_birth_name_data(birth_name_input)

    for line in input:
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
                # The majority of these are junk.
                logging.error(f"Entry with no surname kanji: {data}")
                continue

        # Remove （モデル） etc.
        kanji = regex.sub(r'（.*?）$', '', kanji)
        kanji = kanji.replace(r'・', ' ')
        kanji = regex.sub(r' [一ニ三四五]代$', '', kanji)
        kanji = regex.sub(r'[(（](.*?)[)）]$', '', kanji)

        kana = extract(data, 'kana.value')
        assert kana is not None
        kana = regex.sub(r'\dだいめ$', '', kana)

        kana = kana.replace('・', ' ')
        kana = cast(str, jcconv3.kata2hira(kana))

        kanji = split_kanji_name(kanji, kana)

        lifetime = Lifetime(
            year(extract(data, 'dob.value')), year(extract(data, 'dod.value'))
        )

        namedata = NameData.person(
            kanji, kana, lifetime=lifetime, source=f'wikidata:{item}'
        )

        if gender := gender_ja(extract(data, 'genderLabel.value')):
            namedata.gender = gender

        if item is not None:
            birth_name_data = birth_name.get(item, None)
            if birth_name_data:
                namedata.authenticity = NameAuthenticity.PSEUDO
                if 'birthNameKana' in birth_name_data:
                    kanji = birth_name_data['birthName']
                    kana = birth_name_data['birthNameKana']
                    kanji = split_kanji_name(kanji, kana)
                    namedata.add_subreading(NameData.person(kanji, kana))

        description = extract(data, 'itemDescription.value')
        if description:
            description = regex.sub(r'^Japanese ', '', description, regex.I)
            description = description[0].upper() + description[1:]
            namedata.notes = description

        try:
            namedata.clean_and_validate()
            print(namedata.to_jsonl())
        except ValueError as e:
            logging.error(f"Validation failure: {e}")


def gender_ja(s: str | None) -> Gender:
    if s:
        if s == "男性":
            return Gender.male
        elif s == "女性":
            return Gender.female

    return Gender.unknown
