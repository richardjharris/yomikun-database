import functools

import unicodedata
import romkan
import regex

accents = {
    'a': {'ā', 'â'},
    'i': {'ī', 'î'},
    'u': {'ū', 'û'},
    'e': {'ē', 'ê'},
    'o': {'ō', 'ô'},
}


def remove_accents(s: str) -> str:
    """
    Remove circumflex and macron-based vowel accents from a string,
    replacing them with unaccented versions.
    """
    for letter in accents:
        for accent in accents[letter]:
            s = s.replace(accent, letter)
    return s


def test_remove_accents():
    assert remove_accents("āâīīîūûêēōôô") == "aaiiiuueeooo"


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

    # Remove hyphens, sometimes seen in real world data: 'ke-nichiro'
    romaji = romaji.replace('-', '')

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
