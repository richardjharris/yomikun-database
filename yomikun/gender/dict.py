"""
Builds a gender database from incoming NameData objects and
the data/name_lists.json data from wikipedia.
"""

from __future__ import annotations
import math
import sys
import json
from typing import Iterable, TextIO
import enum
from collections import defaultdict, Counter
from math import sqrt
import logging

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


def load_name_lists(name_list_data: NameLists) -> dict[str, set[ListTitle]]:
    """
    Converts the name list data loaded from JSON file to a mapping
    of kana name -> ListTitle tags (above).
    """
    tags_for_name = defaultdict(set)
    for list_name, list_data in name_list_data.items():
        list_tag = ListTitle(list_name)
        for _page_id, name in list_data.items():
            # Force leading o-macron -> oo
            name = romaji_to_hiragana(name, '大')
            tags_for_name[name].add(list_tag)

    return tags_for_name


def sanity_check_score(score: float, name_lists: set[ListTitle]) -> str | None:
    """
    Check a name's gender `score` against its `name_lists`, as scraped
    from Wikipedia data. Returns an error if they don't match.
    """
    # Sanity check against Wikipedia name lists
    if ListTitle.UNISEX in name_lists:
        # Anything is allowed - some readings are more male than others
        return
    elif ListTitle.MALE in name_lists:
        if score > 0:
            return f'MALE but score is {score}'
    elif ListTitle.FEMALE in name_lists:
        if score < 0:
            return f'FEMALE but score is {score}'
    else:
        # No name list data - ignore
        return


def adjusted_wald_moe(female, male, z=1.96):
    """
    Given male/female counts return the margin of error (0..0.5) from
    the adjusted Wald confidence interval. Default z=1.96 = 95% confidence.
    """
    n = female + male

    if n == 0:
        return 0

    # Use Adjusted Wald: is better for small samples
    # Normally phat is just female/n
    phat = (female + ((z*z)/2)) / (n + (z*z))

    # Work out Margin of Error by applying Wald formula
    margin_of_error = (z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)

    return margin_of_error


def score_from_counts(
    by_kanji: dict[Gender, int],
    by_kana: dict[Gender, int],
) -> tuple[float, float]:
    """
    Given a map of gender -> person count (by kanji+yomi, and then by yomi
    alone) return two values:
     1) Estimated gender [-1, 1]
        Expressed as a value between -1 (male only) .. 0 (unisex) .. 1 (female).
        Values in between represent names that are mostly but not exclusively
        male or female.

     2) Confidence [0,1]
        From 0 (no data, no idea) -> 1 (very very sure)
    """
    # TODO note on by_kana: this is only useful in cases where every
    # use of a given kana is male/female regardless of kanji. Such cases
    # will be picked up by the ML algorithm anyway.
    male = by_kanji[Gender.male]
    female = by_kanji[Gender.female]
    total = male + female

    # First use by_kanji
    if total > 0:
        score = (female / total) * 2 - 1

        margin_of_error = adjusted_wald_moe(female, male)

        # Convert margin of error (0..0.5) to confidence (0..1)
        confidence = 1 - (margin_of_error * 2)

        # Margin of error is more meaningful at the edges (difference between
        # a male/female-only name and unisex) and less meaningful for scores
        # close to 0.5.
        confidence = min(1, confidence * (1.5 - abs(score - 0.5)))

        return score, confidence
    else:
        # Not enough information
        return 0, 0


def make_gender_dict(
    names: Iterable[NameData],
    name_list_data: NameLists,
    dict_out: TextIO,
    weights: str | None,
):
    """
    Build gender dictionary using gender-tagged Person information in `names`
    Output dictionary to `dict_out` (JSON format)
    Save ML model weights to file `weights` is specified.
    """
    counts_kana = defaultdict(Counter)
    counts_kanji = defaultdict(Counter)
    all_names = set()
    model = GenderML(quiet=True)

    tags_for_name = load_name_lists(name_list_data)

    # Count the occurences, per-gender, for each input name.
    # Train the ML model
    for name in names:
        assert 'person' in name.tags

        source = name.source.split(':')[0]

        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            if part.position != NamePosition.mei:
                continue

            counts_kana[part.yomi][gender] += 1
            counts_kanji[part][gender] += 1

            if gender and gender != Gender.unknown:
                model.train(part.kaki, part.yomi, gender == Gender.female)

            # TODO i think counts_kanji covers this
            all_names.add(part)

    # Now do testing
    # As for Sep 11 Sep, about 8.7k names fail testing (!!)
    for test in all_names:
        by_kana = counts_kana[test.yomi]
        by_kanji = counts_kanji[test]
        tags = tags_for_name[test.yomi]

        # ML score is -1 (male) to 1 (female)
        ml_score = model.predict(test.kaki, test.yomi)

        # Count score is the same. Confidence is 0~1.
        # A confidence of 0 means 'no data'
        # A confidence of 1 means 'a lot of data'
        ct_score, ct_confidence = score_from_counts(by_kana, by_kanji)

        # Decide which score to use
        gender_score = ct_score if ct_confidence > 0.5 else ml_score

        # Sanity check score against Wikipedia name lists
        err = sanity_check_score(gender_score, tags)
        if err:
            logging.warning(f"{test} error: {err}")

        print(json.dumps({
            'kaki': test.kaki,
            'yomi': test.yomi,
            'ml_score': ml_score,
            'ct_score': ct_score,
            'ct_confidence': ct_confidence,
            'final_score': gender_score,
            'hits_male': by_kanji[Gender.male],
            'hits_female': by_kanji[Gender.female],
            'hits_unknown': by_kanji[Gender.unknown],
            'err': err,
        }, ensure_ascii=False), file=dict_out)

    if weights:
        model.save(weights)
