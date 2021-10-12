from __future__ import annotations
import romkan
import regex


def romaji_to_hiragana_messy(romaji: str, kanji: str | None = None, leading_o: str = '') -> str:
    """
    Convert romaji string to hiragana. If kanji is supplied, used as
    a hint for converting ō to either ou or oo in limited cases.
    Otherwise it defaults to ou. A common case is wanting to specify
    a leading ō as 'oo' or 'ou': this can be done by passing leading_o='oo'.

    This function should be replaced with romaji_to_hiragana_fullname
    (or _part) where kanji is available, as it will produce better
    results.
    """
    romaji = romaji.lower()

    # Special case to convert ō to oo
    # TODO we now have a better method for this
    if kanji and kanji.startswith(('大', '太')) and \
            romaji.startswith('ō'):
        romaji = romaji.replace('ō', 'oo', 1)
    elif leading_o:
        romaji = romaji.replace('ō', leading_o, 1)

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
    assert romaji_to_hiragana_messy('Sōkokurai Eikichi') == 'そうこくらい えいきち'


def test_gackt():
    assert romaji_to_hiragana_messy('Ōshiro Gakuto') == 'おうしろ がくと'
    assert romaji_to_hiragana_messy('Ōshiro Gakuto', '大城 ガクト') == 'おおしろ がくと'


def test_ota_masanori():
    assert romaji_to_hiragana_messy('Ōta Masanori', '太田') == 'おおた まさのり'


def test_oh():
    assert romaji_to_hiragana_messy('Ryohei Saito') == 'りょへい さいと', \
        'Short os are wrong, but oh has not been converted to ou'

    assert romaji_to_hiragana_messy('Tomohiko TAKAHASHI') == 'ともひこ たかはし'
    assert romaji_to_hiragana_messy('Maki Saitoh') == 'まき さいとう'
    assert romaji_to_hiragana_messy('Kohta Takahashi') == 'こうた たかはし'
    assert romaji_to_hiragana_messy('Koh Aoki') == 'こう あおき'
