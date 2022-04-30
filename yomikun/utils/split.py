"""
Utilities for splitting names where either the kana or kanji
has no space.

This is used by Wikidata/nokana, Daijisen, Koujin, Wikipedia
EN and JA so these importers should be re-run if this code is
updated.

TODO: this only looks at jamdict (JMnedict) which is missing
a number of names e.g. 吉田＝よしだ. Using our own data would
improve things.

TODO: we try to match biggest surname, then biggest given name.
In reality if we can match both sides we should prefer that?
  An example is 和田慎二 (wada shinji)
  jmnedict matches 和田 as わだし only
  therefore we split, but んじ is not valid?
"""

from __future__ import annotations

import pytest
import romkan

import yomikun.utils.name_dict as name_dict


def split_kanji_name_romaji(kanji: str, romaji: str) -> str:
    """
    Splits a kanji name using romaji (which could be ambiguous)
    Uses RomajiDB to find a split point, tolerating the ambiguity.

    Returns kanji as-is if unable to split.
    """
    if len(romaji.split()) != 2:
        # romaji not in two parts - can't split
        return kanji

    if len(kanji.split()) >= 2:
        # already split
        return kanji

    sei, mei = romaji.split()
    split_point = find_split_point(sei, mei, kanji, romaji=True)
    if split_point is None:
        return kanji
    else:
        return f"{kanji[0:split_point]} {kanji[split_point:]}"


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
    if split_point is None:
        return kaki
    else:
        return f"{kaki[0:split_point]} {kaki[split_point:]}"


def split_kana_name(kaki: str, yomi: str) -> str:
    """
    Given written form (kaki) WITH spaces, and read form (yomi)
    without, split yomi into two parts that match the kanji,
    and return the parts joined with a space.

    Returns yomi as-is if unable to split.
    """
    if len(kaki.split()) != 2:
        raise ValueError('kaki must contain two names')
    if len(yomi.split()) != 1:
        raise ValueError('yomi must contain no spaces')

    sei, mei = kaki.split()
    split_point = find_kana_split_point(sei, mei, yomi)
    if split_point is None:
        return yomi
    else:
        return f"{yomi[0:split_point]} {yomi[split_point:]}"


def find_split_point(
    sei: str,
    mei: str,
    kanji: str,
    romaji: bool = False,
    reverse: bool = True,
) -> int | None:
    """
    Given the surname and first name (in kana), and the combined kanji,
    split the kanji to separate the two name portions. Return the number
    of chars in `kanji` that corresponds to the surname.

    If `romaji` is passed, assumes sei/mei are romaji and performs
    fuzzy kana conversion internally. With `reverse ` (default True), is also
    able to reverse romaji that is the wrong way around.

    If we can't do it for some reason, returns None.
    """
    # TODO RomajiDB should have multiple readings, else we might fail to
    #      split for some names.
    # TODO when romaji=False we could still use our own data, it's better.
    # Try to match the largest string first.
    for chars in reversed(range(1, len(kanji))):
        kanji_prefix = kanji[0:chars]
        if name_dict.match_name(kanji_prefix, sei, sei=True, romaji=romaji):
            return chars

    # Try to match forenames instead
    for chars in range(1, len(kanji)):
        kanji_suffix = kanji[chars:]
        if name_dict.match_name(kanji_suffix, mei, sei=False, romaji=romaji):
            return chars

    if romaji and reverse:
        # Try swapping mei/sei
        return find_split_point(mei, sei, kanji, romaji=True, reverse=False)

    return None


def find_kana_split_point(sei: str, mei: str, kana: str) -> int | None:
    """
    Given the surname and first name (in KANJI), and the combined kana,
    split the kana to separate the two name portions. Return the number
    of chars in `kana` that corresponds to the surname.

    If we can't do it for some reason, returns None.
    """
    # This is literally the above method but with kana/kanji swapped around.
    # Might become more complicated later, as kana is more ambiguous.

    # Try to match the largest string first.
    for chars in reversed(range(1, len(kana))):
        kana_prefix = kana[0:chars]
        results = name_dict.find_surname(kana_prefix)

        for result in results:
            if sei in result.kanji:
                return chars

    # Try to match forenames instead
    for chars in range(1, len(kana)):
        kana_suffix = kana[chars:]
        results = name_dict.find_given_name(kana_suffix)

        for result in results:
            if mei in result.kanji:
                return chars

    return None


def try_to_swap_names(kanji: str, kana: str) -> tuple[str, str]:
    """
    Given split kanji/kana, check them against the JMnedict data and try
    to swap them if it makes more sense.
    """
    # The current method joins the kanji together then tries to split it.
    # This requires there to be JMnedict data.
    # TODO: A better method would just check our existing surname/mei/sei data.
    # TODO: Why do we return kanji here?
    old_kanji, old_kana = kanji, kana
    kanji = kanji.replace(' ', '')

    kanji = split_kanji_name(kanji, kana)

    if len(kanji.split()) == 1:
        # Try the other way around
        kana = ' '.join(reversed(kana.split()))
        kanji = split_kanji_name(kanji, kana)

        if len(kanji.split()) == 1:
            # Revert back to the original
            kanji, kana = old_kanji, old_kana

    return kanji, kana


# Format: surname (kana), given name (kana), surname (kanji), given name (kana)
# Tests are generated by removing the spaces in 1) yomi 2) kaki and checking if
# the computed split point would add the space back correctly.
tests = [
    "まつだいら ただなお 松平 忠直",
    "ゆうき ひでやす 結城 秀康",
    "なんじょう ぶんゆう 南条 文雄",
    "なわ ながとし 名和 長年",
    "なるせ みきお 成瀬 巳喜男",
    "ひとみ きぬえ 人見 絹枝",
    "ばば つねご 馬場 恒吾",
    "ひなつ こうのすけ 日夏 耿之介",
    "こいずみ やくも 小泉 八雲",
    "さくらだ いちろう 桜田 一郎",
    "とみた けいせん 富田 渓仙",
    "あらし さんえもん 嵐 三右衛門",
    "ありさか なりあきら 有坂 成章",
    "おおもり よしたろう 大森 義太郎",
    "おぐま ひでお 小熊 秀雄",
    "かたくら かねたろう 片倉 兼太郎",
    "たけぞえ しんいちろう 竹添 進一郎",
    "たけだ ゆうきち 武田 祐吉",
    "たじみ くになが 多治見 国長",
    "たなべ はじめ 田辺 元",
    "つじ じゅん 辻 潤",
    "つじ ぜんのすけ 辻 善之助",
    "つだ すけひろ 津田 助広",
    "なつめ そうせき 夏目 漱石",
    # SUPER HARD MODE
    "あいしんかくら い 愛新覚羅 維",
    # Chinese? Can identify these via 中国 after the year.
    # ("き ゆうこう 帰有光", 1
    # ("そ じゅん 蘇洵", 1
    # This requires a forename lookup
    "あびる えいさぶろう 阿比類 鋭三郎",
    "まや みねお 魔夜 峰央",
]


@pytest.mark.parametrize('test', tests)
def test_split_point_kanji(test):
    sei_yomi, mei_yomi, sei_kaki, mei_kaki = test.split(' ')

    result = find_split_point(sei_yomi, mei_yomi, f"{sei_kaki}{mei_kaki}")
    assert result == len(sei_kaki)


@pytest.mark.parametrize('test', tests)
def test_split_point_kana(test):
    sei_yomi, mei_yomi, sei_kaki, mei_kaki = test.split(' ')

    result = find_kana_split_point(sei_kaki, mei_kaki, f"{sei_yomi}{mei_yomi}")
    assert result == len(sei_yomi)


@pytest.mark.parametrize('test', tests)
def test_split_point_romaji(test):
    sei_yomi, mei_yomi, sei_kaki, mei_kaki = test.split(' ')

    sei = romkan.to_roma(sei_yomi)
    mei = romkan.to_roma(mei_yomi)
    kanji = sei_kaki + mei_kaki

    result = find_split_point(sei, mei, kanji, romaji=True)
    assert result == len(sei_kaki)

    result_reversed = find_split_point(mei, sei, kanji, romaji=True)
    assert result == result_reversed


def test_split_romaji_ambiguous():
    assert split_kanji_name_romaji("北条大峯", "hojo omine") == "北条 大峯"
    assert split_kanji_name_romaji("北条 大峯", "hojo omine") == "北条 大峯", 'already split'
    assert split_kanji_name_romaji("北条大峯", "hojoomine") == "北条大峯", 'romaji not split'


def test_split_kanji_name():
    assert split_kanji_name("田辺元", "たなべ はじめ") == "田辺 元"
    assert split_kanji_name("田辺元", "わか わか") == "田辺元", 'weird yomi'
    assert split_kanji_name("田辺 元", "たなべ はじめ") == "田辺 元", 'aleady split'
    assert split_kanji_name("田辺元", "たなべはじめ") == "田辺元", 'kanji not split'


def test_split_kana_name():
    assert split_kana_name("田辺 元", "たなべはじめ") == "たなべ はじめ"
    assert split_kana_name("田辺 元", "たなかしゅん") == "たなかしゅん", 'weird yomi'
    with pytest.raises(ValueError):
        assert split_kana_name("田辺 元", "たなべ はじめ") == "たなべ はじめ", 'already split'
    with pytest.raises(ValueError):
        assert split_kana_name("田辺元", "たなかはじめ") == "たなかはじめ", 'kana not split'
