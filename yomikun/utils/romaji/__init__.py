from __future__ import annotations
import logging

import regex
import romkan

from yomikun.utils.name_dict import NameDict
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy
from yomikun.utils.romaji.helpers import romaji_key


def romaji_to_hiragana_strict(romaji: str) -> str:
    """
    Converts romaji to hiragana. Romaji must be normalised - no ambiguous
    vowels, apostrophe where needed, etc, no macrons.
    """
    romaji = romaji.lower()
    if not regex.match(r"^[a-z' ]*$", romaji):
        raise ValueError(f"Input '{romaji}' has weird characters in it. Yuk!")

    return romkan.to_hiragana(romaji)


def romaji_to_hiragana_fullname(romaji: str, kanji: str) -> str | None:
    """
    Convert ambiguous romaji string to hiragana, using kanji as a guide to
    determine length of vowels (Yusuke -> Yuusuke and so on).

    This is done by looking up the kanji word in the JMnedict dictionary
    e.g. 進次郎 -> しんじろう, if romaji is 'shinjiro' we know to add a -u.
    """
    # Only works if we have two parts (surname + given name)
    if len(romaji.split()) != 2 or len(kanji.split()) != 2:
        return None

    new_sei = romaji_to_hiragana_part(
        romaji.split()[0], kanji.split()[0], sei=True)
    new_mei = romaji_to_hiragana_part(
        romaji.split()[1], kanji.split()[1], sei=False)

    if new_sei is None or new_mei is None:
        return None

    return f"{new_sei} {new_mei}"


def romaji_to_hiragana_part(romaji: str, kanji: str, sei: bool) -> str | None:
    """
    Convert ambiguous romaji name (sei/mei) to hiragana using the kanji as a
    guide to determine length of vowels.
    """
    logging.debug(
        f"[romaji_to_hiragana_part] ({romaji}, {kanji}, {'SEI' if sei else 'MEI'})")

    if sei:
        matches = NameDict.find_surname(kanji)
    else:
        matches = NameDict.find_given_name(kanji)

    if not matches:
        logging.debug('No matches, returning')
        return

    key = romaji_key(romaji)
    hits = []
    for match in matches:
        if not any(kanji == k for k in match.kanji):
            continue

        for kana in match.kana:
            match_key = romaji_key(romkan.to_roma(kana))
            matches_target = romaji_key(romkan.to_roma(kana)) == key
            if matches_target:
                hits.append(kana)

            logging.debug(
                f"[rom->hira] input({romaji}, {kanji}, {'Sei' if sei else 'Mei'}, {key}) match({kana}, {match_key}) => {matches_target}")

    # Pick the longest one (for now).
    # However given the choice between おごお and おごう (-oo and -ou), pick -ou, as -oo
    # seems very rare.
    # TODO: (HACK!) this can go away once we use frequency information
    if hits:
        hits.sort(key=len, reverse=True)
        best = hits[0]

        # Prefer おごう over おごお
        best_roma = romkan.to_roma(best)
        if len(hits) > 1 and len(hits[0]) == len(hits[1]) and len(hits[0]) > 2 and best_roma[-1] == best_roma[-2]:
            best = hits[1]

        logging.debug(f"Returning {best} from {hits}")
        return best
    else:
        return


def test_hiragana_part():
    assert romaji_to_hiragana_part('Saito', '齋藤', sei=True) == 'さいとう'
    assert romaji_to_hiragana_part('Ohashi', '大橋', sei=True) == 'おおはし'
    assert romaji_to_hiragana_part('Yuki', '祐紀', sei=False) == 'ゆうき'
