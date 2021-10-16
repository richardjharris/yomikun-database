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
    # Apostrophes/hyphens are usually used to avoid ambiguity e.g. 'Tomo-o' (ともお),
    # "Ken'ichi" (けんいち) so use them. We ignore kanji in this case.
    parts = regex.split(r"['-]", romaji)
    if len(parts) > 1:
        return ''.join(romaji_to_hiragana_messy(part) for part in parts)

    romaji = romaji.lower()

    # Special case to convert ō to oo
    if start_o := regex.search(r'^(ō|oh|ow)', romaji):
        replacement = None
        if leading_o:
            replacement = leading_o
        elif kanji and kanji.startswith(('大', '太')):
            replacement = 'oo'
        elif kanji and kanji.startswith(('王')):
            replacement = 'ou'

        if replacement:
            romaji = romaji.replace(start_o[0], replacement, 1)

    # TODO We don't try to handle ē -> ei. We could use a kanji dictionary.

    romaji = regex.sub(r'ow$', 'oh', romaji)
    romaji = regex.sub(r'm(?=[bpm])', 'n', romaji)
    romaji = romaji.replace('l', 'r')

    # Replace 'oh' sound unless the h is part of a new mora.
    # Sometimes (less often) this could be 'oo', but oh well.
    romaji = regex.sub(r'oh(?![aiueoy])', 'ou', romaji)

    # Convert macrons to long vowels. Again, we don't know exactly how
    # to convert them so we guess.
    romaji = romaji.replace('ō', 'ou')
    romaji = romaji.replace('ā', 'aa')
    romaji = romaji.replace('ē', 'ee')
    romaji = romaji.replace('ū', 'uu')

    # Special case for a common name ending
    if romaji.endswith('ro') and kanji and kanji.endswith('郎'):
        romaji += 'u'

    return romkan.to_hiragana(romaji)


def test_basic():
    assert romaji_to_hiragana_messy('Sōkokurai Eikichi') == 'そうこくらい えいきち'


def test_gackt():
    assert romaji_to_hiragana_messy('Ōshiro Gakuto') == 'おうしろ がくと'
    assert romaji_to_hiragana_messy('Ōshiro Gakuto', '大城 ガクト') == 'おおしろ がくと'


def test_ota_masanori():
    assert romaji_to_hiragana_messy('Ōta Masanori', '太田') == 'おおた まさのり'


def test_ow():
    assert romaji_to_hiragana_messy('Satow') == 'さとう'


def test_shumpei():
    assert romaji_to_hiragana_messy('Shumpei') == 'しゅんぺい'
    assert romaji_to_hiragana_messy('SINBA') == 'しんば'


def test_oh():
    assert romaji_to_hiragana_messy('Ryohei Saito') == 'りょへい さいと', \
        'Short os are wrong, but oh has not been converted to ou'

    assert romaji_to_hiragana_messy('Tomohiko TAKAHASHI') == 'ともひこ たかはし'
    assert romaji_to_hiragana_messy('Maki Saitoh') == 'まき さいとう'
    assert romaji_to_hiragana_messy('Kohta Takahashi') == 'こうた たかはし'
    assert romaji_to_hiragana_messy('Koh Aoki') == 'こう あおき'


def test_hyphen_etc():
    assert romaji_to_hiragana_messy('Tomo-o') == 'ともお'
    assert romaji_to_hiragana_messy("Ken'ichi") == 'けんいち'
