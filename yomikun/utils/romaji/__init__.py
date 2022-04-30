"""
Utilities for converting romaji names to hiragana, using an external
dictionary to handle ambiguous romaji.
"""
from __future__ import annotations
import logging

import regex
import romkan

from yomikun.utils.romaji.helpers import romaji_key
from yomikun.romajidb.db import romajidb


def romaji_to_hiragana_strict(romaji: str) -> str:
    """
    Converts romaji to hiragana strictly, i.e. it is assumed that the romaji
    will correctly use long and short vowels to match the kana equivalent,
    apostrophes if needed, and no macrons.

    Returns the hiragana form of the name.
    """
    romaji = romaji.lower()
    if not regex.match(r"^[a-z' ]*$", romaji):
        raise ValueError(f"Input '{romaji}' has weird characters in it. Yuk!")

    # Fix 'Itchiku' (いっちく、一竹)
    romaji = romaji.replace("tch", "cch")

    return romkan.to_hiragana(romaji)


def romaji_to_hiragana_fullname(romaji: str, kanji: str) -> str | None:
    """
    Convert ambiguous romaji string to hiragana, using kanji as a guide to
    determine length of vowels (Yusuke -> Yuusuke and so on).

    This is done by looking up the kanji word in the RomajiDB dictionary
    e.g. 進次郎 -> しんじろう, if romaji is 'shinjiro' we know to add a -u.
    """
    # Only works if we have two parts (surname + given name)
    if len(romaji.split()) != 2 or len(kanji.split()) != 2:
        return None

    new_sei, new_mei = romaji_to_hiragana_fullname_parts(romaji, kanji)

    if new_sei is None or new_mei is None:
        return None

    return f"{new_sei} {new_mei}"


def romaji_to_hiragana_fullname_parts(
    romaji: str, kanji: str
) -> tuple[str | None, str | None]:
    """
    Converts ambiguous romaji full name to hiragana, using kanji as a guide. Both [romaji]
    and [kanji] must have two name components. Returns the hiragana form of the name as
    a tuple of two name components.
    """
    new_sei = romaji_to_hiragana_part(romaji.split()[0], kanji.split()[0], sei=True)
    new_mei = romaji_to_hiragana_part(romaji.split()[1], kanji.split()[1], sei=False)

    return new_sei, new_mei


def romaji_to_hiragana_part(romaji: str, kanji: str, sei: bool) -> str | None:
    """
    Convert ambiguous romaji name (sei/mei) to hiragana using the kanji as a
    guide to determine length of vowels.
    """
    key = romaji_key(romaji)
    kana = romajidb().get(kanji, key, "sei" if sei else "mei")

    logging.debug(
        f"[r2h:part] ({romaji}[{key}], {kanji}, {'SEI' if sei else 'MEI'}) => {kana}"
    )

    if kana:
        # We are done
        return kana
    else:
        # Give up, as the name as ambiguous.
        return


def test_hiragana_part():
    assert romaji_to_hiragana_part("Saito", "齋藤", sei=True) == "さいとう"
    assert romaji_to_hiragana_part("Ohashi", "大橋", sei=True) == "おおはし"
    assert romaji_to_hiragana_part("Yuki", "祐紀", sei=False) == "ゆうき"
