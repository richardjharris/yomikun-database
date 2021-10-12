from __future__ import annotations
import unicodedata
import functools
import logging

import regex
import romkan

from yomikun.utils.name_dict import NameDict


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
    if sei:
        matches = NameDict.find_surname(kanji)
    else:
        matches = NameDict.find_given_name(kanji)

    print(romaji, kanji, sei, matches)
    if not matches:
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

            logging.info(
                f"[rom->hira] input({romaji}, {kanji}, {'Sei' if sei else 'Mei'}, {key}) match({kana}, {match_key}) => {matches_target}")

    # Pick the longest one (for now)
    if hits:
        hits.sort(key=len)
        return hits[-1]
    else:
        return


def test_hiragana_part():
    assert romaji_to_hiragana_part('Saito', '齋藤', sei=True) == 'さいとう'
    assert romaji_to_hiragana_part('Ohashi', '大橋', sei=True) == 'おおはし'
    assert romaji_to_hiragana_part('Yuki', '祐紀', sei=False) == 'ゆうき'


accents = {
    'a': {'ā', 'â'},
    'i': {'ī', 'î'},
    'u': {'ū', 'û'},
    'e': {'ē', 'ê'},
    'o': {'ō', 'ô'},
}


def remove_accents(s: str) -> str:
    for letter in accents:
        for accent in accents[letter]:
            s = s.replace(accent, letter)
    return s


@functools.cache
def romaji_key(romaji: str) -> str:
    """
    Returns a romaji key that allows ambiguous romajis to be compared.
    Example romaji forms for ごとう　ゆうすけ:
      Goto Yusuke          # No long vowels
      Gotō Yūsuke          # Macron
      Gotô Yûsuke          # Circumflex
      Gotou Yuusuke        # Long vowels
      Gotoh Yuhsuke        # 'oh' form (and 'eh' for ei)

    Our approach is to collapse oh, ou and o into simply 'o' and the
    same for eh, ei and e; and collapse any number of i, a or u into
    one. (Initially we just collapsed all vowels, but 斎藤 has entries
    for both さいとう and さという, which would both become 'sato')
    (Ignoring whether さという is even a sensible entry - it is in the
    JMnedict)
    """
    romaji = romaji.lower()
    romaji = unicodedata.normalize('NFC', romaji)
    romaji = remove_accents(romaji)

    # Normalise romaji forms (hu/fu, sya/sha)
    romaji = romkan.to_roma(romkan.to_kana(romaji))

    # Remove apostrophe (used to disambiguate, e.g. 万葉 is man'you,
    # not ma'nyou). We don't care about this because it's unlikely that
    # a name will have two ambiguous kana forms but the same kanji.
    romaji = romaji.replace("'", '')

    # Collapse vowels into one
    romaji = regex.sub(r'(oh(?![aiueo])|ou|oo)', 'o', romaji)
    romaji = regex.sub(r'(eh(?![aiueo])|ei|ee)', 'e', romaji)
    romaji = regex.sub(r'([aiu])\1+', '\\1', romaji)

    return romaji


def test_romaji_key():
    assert romaji_key('yuusuke') == romaji_key('yusuke')
    assert romaji_key("man'you") == romaji_key("manyou")
    assert romaji_key("goto") == romaji_key("gotou")
    assert romaji_key("otani") == romaji_key("ohtani")
    assert romaji_key("kireh") == romaji_key("kirei")
    assert romaji_key("takashi") != romaji_key("takeshi")
    assert romaji_key("gotou") != romaji_key("botou")
    assert romaji_key("Yūsuke") == romaji_key("yuusuke")
    assert romaji_key("Yûsuke") == romaji_key("yuusuke")
    assert romaji_key("ooi") != romaji_key("aoi")
    assert romaji_key("shiina") == romaji_key("shina")
    assert romaji_key('saitou') != romaji_key('satoiu')
    assert romaji_key('sito') != romaji_key('saito')
