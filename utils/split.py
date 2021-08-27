from __future__ import annotations
import re

import jamdict
import pytest

# TODO: turn on memory_mode outside of test mode
# TODO: we use jamdict-data for now
jam = jamdict.Jamdict(
    memory_mode=False,
)
assert jam.has_jmne()


def split_kanji_name(kaki: str, yomi: str) -> str:
    """
    Given written form (kaki) with no spaces and read form (yomi)
    with spaces, split kaki into two parts that match the yomi
    and return the parts joined with a space.

    Returns kaki as-is if unable to split.
    """
    if len(yomi.split()) != 2:
        # yomi not in two parts - can't split
        return kaki

    if len(kaki.split()) >= 2:
        # already split
        return kaki

    sei, mei = yomi.split()
    split_point = find_split_point(sei, mei, kaki)
    if split_point == -1:
        return kaki
    else:
        return f"{kaki[0:split_point]} {kaki[split_point:]}"


def find_split_point(sei: str, mei: str, kanji: str) -> int | None:
    """
    Given the surname and first name (in kana), and the combined kanji,
    split the kanji to separate the two name portions. Return the number
    of chars in `kanji` that corresponds to the surname.

    If we can't do it for some reason, returns None.
    """
    def has_sense(senses: list, keyword: str):
        """
        Look into the senses object to find a sense entry
        with a name_type matching the given `keyword`.

        keyword should be 'place', 'surname', 'fem' etc.
        """
        for sense in senses:
            for name_type in sense.name_type:
                if name_type == keyword:
                    return True
        return False

    # Try to match the largest string first.
    for chars in reversed(range(1, len(kanji))):
        kanji_prefix = kanji[0:chars]
        result = jam.lookup(
            query=kanji_prefix, strict_lookup=True, lookup_chars=False)

        for name in result.names:
            if not has_sense(name.senses, 'surname'):
                continue

            # Gotcha: basic string comparison won't work, must
            # use text attribute
            kana_forms = [kf.text for kf in name.kana_forms]

            if sei in kana_forms:
                return chars

    return None


tests = [
    ("まつだいら‐ただなお【松平忠直】", 2),
    ("ゆうき‐ひでやす【結城秀康】", 2),
    ("なんじょう‐ぶんゆう【南条文雄】", 2),
    ("なわ‐ながとし【名和長年】", 2),
    ("なるせ‐みきお【成瀬巳喜男】", 2),
    ("ひとみ‐きぬえ【人見絹枝】", 2),
    ("ばば‐つねご【馬場恒吾】", 2),
    ("ひなつ‐こうのすけ【日夏耿之介】", 2),
    ("こいずみ‐やくも【小泉八雲】", 2),
    ("さくらだ‐いちろう【桜田一郎】", 2),
    ("とみた‐けいせん【富田渓仙】", 2),
    ("あらし‐さんえもん【嵐三右衛門】", 1),
    ("ありさか‐なりあきら【有坂成章】", 2),
    ("おおもり‐よしたろう【大森義太郎】", 2),
    ("おぐま‐ひでお【小熊秀雄】", 2),
    ("かたくら‐かねたろう【片倉兼太郎】", 2),
    ("たけぞえ‐しんいちろう【竹添進一郎】", 2),
    ("たけだ‐ゆうきち【武田祐吉】", 2),
    ("たじみ‐くになが【多治見国長】", 3),
    ("たなべ‐はじめ【田辺元】", 2),
    ("つじ‐じゅん【辻潤】", 1),
    ("つじ‐ぜんのすけ【辻善之助】", 1),
    ("つだ‐すけひろ【津田助広】", 2),
    ("なつめ‐そうせき【夏目漱石】", 2),
    # SUPER HARD MODE
    ("あいしんかくら‐い【愛新覚羅維】", 4),
    # Chinese? Can identify these via 中国 after the year.
    # ("き‐ゆうこう【帰有光】", 1),
    # ("そ‐じゅん【蘇洵】", 1),
]


@ pytest.mark.parametrize('test', tests)
def test_split_name(test):
    dict_entry, expected_split_point = test
    m = re.fullmatch(r'(.*?)‐(.*?)【(.*?)】', dict_entry)
    assert m is not None

    assert find_split_point(m[1], m[2], m[3]) == expected_split_point
