"""
Builds a gender database from incoming NameData objects and
the data/name_lists.json data from wikipedia.

# Objectives

To be able to answer questions like:

 * given a kanji or kana given name, what is the likely gender?
 * what are the most unisex names?
 * what kanji versions of a particular kana name are most often
   associated with men or women?

For improving our data:

 * what names have zero or very few gender-tagged results?

# Ideas

 - Improve male tagging - 男優 etc. Categories should override
   anything else.

 - Try to remove FPs via person merging
   房之介 appears in wikidata as female (incorrectly) and male in
   wikipedia_en, _ja (correctly).

 - Using tagged data find the most common kanji for male/female names.

 - For each first name in wikipedia_ja (for example) try to compute
   the gender.

    Resources: data/name_lists.json (reading)
               average gender for kana reading
               average gender for kanji reading (*)
               guess based on kanji inside
               guess based on name length (4+ is usually male)
               manual overrides

    For cross checking: baby names site, namegen, JA wikipedia pages

    We can then compute a name dictionary which can be looked up
    independently of everything else.

    Where the results differ from reality, we tweak the algorithm.
"""
from __future__ import annotations
from typing import Iterable
import enum
from collections import defaultdict, Counter
import logging

from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.utils.romaji import romaji_to_hiragana

from yomikun.models import NameData
from yomikun.loader.aggregator import Aggregator
from yomikun.loader.models import Gender, NamePosition

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
        if source not in ('wikidata', 'wikidata-nokana', 'wikipedia_en', 'wikipedia_ja'):
            continue

        # Instruct Aggregator that these are full names
        name.add_tag('person')
        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            if part.position != NamePosition.mei:
                continue

            counts_kana[part.yomi][gender] += 1
            counts_kanji[part][gender] += 1

            # TBD name part does not include fictional, so we have to discard both the real
            # name and fictional name in this case..
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

        if err:
            logging.info(
                f"{test.kaki} [m:{by_kanji[Gender.male]} f:{by_kanji[Gender.female]} u:{by_kanji[Gender.unknown]}] " +
                f"({test.yomi}) [m:{by_kana[Gender.male]} f:{by_kana[Gender.female]} u:{by_kana[Gender.unknown]}] " +
                f"{', '.join(tag.name for tag in tags)}"
            )
            logging.info(err)
        pass
