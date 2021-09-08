from __future__ import annotations

import romkan


def romaji_to_hiragana(romaji: str, kanji: str | None = None):
    """
    Convert romaji string to hiragana. If kanji is supplied, used as
    a hint for converting ō to either ou or oo in limited cases.
    Otherwise it defaults to ou.
    """
    romaji = romaji.lower()

    # Special case to convert ō to oo
    if kanji and kanji.startswith('大') and romaji.startswith('ō'):
        romaji.replace('ō', 'oo', 1)

    # TODO We don't handle ē -> ei at this time. Kanji name dictionary
    # may help here.

    # Convert macrons to long vowels
    romaji = romaji.replace('ō', 'ou')
    romaji = romaji.replace('ā', 'aa')
    romaji = romaji.replace('ē', 'ee')
    return romkan.to_hiragana(romaji)


def test_basic():
    assert romaji_to_hiragana('Sōkokurai Eikichi') == 'そうこくらい えいきち'


def test_gackt():
    assert romaji_to_hiragana('Ōshiro Gakuto') == 'おうしろ がくと'
    assert romaji_to_hiragana('Ōshiro Gakuto', '大城 ガクト') == 'おうしろ がくと'
