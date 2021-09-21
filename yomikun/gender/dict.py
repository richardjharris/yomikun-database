"""
Builds a gender database from incoming NameData objects and
the data/name_lists.json data from wikipedia.
"""

from __future__ import annotations
from typing import Iterable
import enum
from collections import defaultdict, Counter

from yomikun.gender.ml import GenderML
from yomikun.loader.aggregator import Aggregator
from yomikun.loader.models import Gender, NamePosition
from yomikun.models import NameData
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.utils.romaji import romaji_to_hiragana


NameLists = dict[str, dict[str, str]]


class ListTitle(str, enum.Enum):
    MALE = 'Japanese masculine given names'
    FEMALE = 'Japanese feminine given names'
    UNISEX = 'Japanese unisex given names'
    SURNAME = 'Japanese-language surnames'


def make_gender_dict(names: Iterable[NameData], name_lists: NameLists):
    counts_kana = defaultdict(Counter)
    counts_kanji = defaultdict(Counter)
    test_names = set()
    model = GenderML(quiet=True)

    # Load name lists
    name_list_tags = defaultdict(set)
    for list_name, list_data in name_lists.items():
        list_tag = ListTitle(list_name)
        for _page_id, name in list_data.items():
            # Force leading o-macron -> oo
            name = romaji_to_hiragana(name, '大')
            name_list_tags[name].add(list_tag)

    for name in names:
        source = name.source.split(':')[0]
        # TBD do this better
        if source not in ('wikidata', 'wikidata-nokana', 'wikipedia_en', 'wikipedia_ja', 'custom', 'researchmap'):
            continue

        # Instruct Aggregator that these are full names
        name.add_tag('person')
        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            if part.position != NamePosition.mei:
                continue

            counts_kana[part.yomi][gender] += 1
            counts_kanji[part][gender] += 1

            if gender and gender != Gender.unknown:
                model.train(part.kaki, part.yomi, gender == Gender.female)

            # TBD name part does not include fictional, so we have to discard both the real
            # name and fictional name in this case.. (??)
            if source == 'wikipedia_ja' and name.authenticity == NameAuthenticity.REAL:
                test_names.add(part)

    # Now do testing
    # As for Sep 11 Sep, about 8.7k names fail testing (!!)
    for test in test_names:
        by_kana = counts_kana[test.yomi]
        by_kanji = counts_kanji[test]
        tags = name_list_tags[test.yomi]
        err = None
        perc = None

        # ML score is -1 (male) to 1 (female), adjust to 'male %'
        prediction = model.predict(test.kaki, test.yomi)

        # First use by_kanji
        if by_kanji[Gender.male] > 0 or by_kanji[Gender.female] > 0:
            perc = by_kanji[Gender.male] / \
                (by_kanji[Gender.male] + by_kanji[Gender.female])

        elif by_kana[Gender.male] > 0 or by_kana[Gender.female] > 0:
            # Try kana
            perc = by_kana[Gender.male] / \
                (by_kana[Gender.male] + by_kana[Gender.female])
        else:
            # We don't know
            perc = None
            err = f"No data"

        if perc is not None:
            # Check against the tags
            if ListTitle.UNISEX in tags:
                # Anything is allowed - some readings are more male than others
                # TBD maybe check the kana counts
                pass
            elif ListTitle.MALE in tags:
                if perc < 0.9:
                    err = f'MALE but perc is {perc}'
            elif ListTitle.FEMALE in tags:
                if perc > 0.1:
                    err = f'FEMALE but perc is {perc}'
            else:
                # No name list data - ignore
                pass

        print("\t".join([
            test.kaki,
            str(by_kanji[Gender.male]),
            str(by_kanji[Gender.female]),
            str(by_kanji[Gender.unknown]),
            str(by_kanji[Gender.male] +
                by_kanji[Gender.female] + by_kanji[Gender.unknown]),
            test.yomi,
            str(by_kana[Gender.male]),
            str(by_kana[Gender.female]),
            str(by_kana[Gender.unknown]),
            str(by_kana[Gender.male] +
                by_kana[Gender.female] + by_kana[Gender.unknown]),
            str(perc),
            str(prediction),
            ', '.join(tag.name for tag in tags),
            err if err else ''
        ]))
