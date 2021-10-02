from __future__ import annotations

import regex
import romkan


def romaji_to_hiragana(romaji: str, kanji: str | None = None) -> str:
    """
    Convert romaji string to hiragana. If kanji is supplied, used as
    a hint for converting ō to either ou or oo in limited cases.
    Otherwise it defaults to ou.
    """
    romaji = romaji.lower()

    # Special case to convert ō to oo
    # TODO we now have a better method for this
    if kanji and kanji.startswith(('大', '太')) and \
            romaji.startswith('ō'):
        romaji = romaji.replace('ō', 'oo', 1)

    # TODO We don't handle ē -> ei at this time. Kanji name dictionary
    # may help here.

    # Replace 'oh' sound unless the h is part of a new mora.
    romaji = regex.sub(r'oh(?![aiueo])', 'ou', romaji)

    # Convert macrons to long vowels
    romaji = romaji.replace('ō', 'ou')
    romaji = romaji.replace('ā', 'aa')
    romaji = romaji.replace('ē', 'ee')
    romaji = romaji.replace('ū', 'uu')
    return romkan.to_hiragana(romaji)


def test_basic():
    assert romaji_to_hiragana('Sōkokurai Eikichi') == 'そうこくらい えいきち'


def test_gackt():
    assert romaji_to_hiragana('Ōshiro Gakuto') == 'おうしろ がくと'
    assert romaji_to_hiragana('Ōshiro Gakuto', '大城 ガクト') == 'おおしろ がくと'


def test_ota_masanori():
    assert romaji_to_hiragana('Ōta Masanori', '太田') == 'おおた まさのり'


def test_oh():
    assert romaji_to_hiragana('Ryohei Saito') == 'りょへい さいと', \
        'Short os are wrong, but oh has not been converted to ou'

    assert romaji_to_hiragana('Tomohiko TAKAHASHI') == 'ともひこ たかはし'
    assert romaji_to_hiragana('Maki Saitoh') == 'まき さいとう'
    assert romaji_to_hiragana('Kohta Takahashi') == 'こうた たかはし'
    assert romaji_to_hiragana('Koh Aoki') == 'こう あおき'


def romaji_to_hiragana_fullname(romaji: str, kanji: str) -> str | None:
    """
    Convert romaji string to hiragana, using kanji as a guide to
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
    Convert a romaji name (sei/mei) to hiragana using the kanji as a
    guide to determine length of vowels.
    """
    # Method:
    # 1. Remove all existing long vowels
    # 2. Look up kanji in jamdict
    # 3. For each result, remove all existing long vowels
    #     - if it matches, use that result
    #     - favour longest match if multiple

    kana = romaji_to_hiragana(romaji)

    return kana


def test_hiragana_part():
    assert romaji_to_hiragana_part('Saito', '齋藤', False) == 'さいとう'
