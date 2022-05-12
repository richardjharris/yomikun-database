import functools
import unicodedata

import regex
import romkan

# Romaji keys where the 'h' is part of the vowel and should
# be removed, e.g. 'ohishi' (おおいし) vs. 'ohashi' (おおはし)
REMOVE_VOWEL_H = {
    'ohae': 'oae',
    'ohe': 'oe',
    'ohi': 'oi',
    'ohike': 'oike',
    'ohishi': 'oishi',
    'ohiwa': 'oiwa',
    'ohyama': 'oyama',
    'ohya': 'oya',
    'kohyama': 'koyama',
    'ohizumi': 'oizumi',
    'ohoka': 'oka',
    'ohori': 'ori',
    'ohuchi': 'ouchi',
    'ohue': 'ooue',
    'ohura': 'oura',
    'yuhya': 'yuya',
    'yohichi': 'yoichi',
}

ACCENTS = {
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
    # Treat ōu specially, so that 'ōue' and 'ooue' both resolve to 'oue'
    # as one would expect. Otherwise 'ōue' becomes 'oe'.
    s = s.replace('ōu', 'oou')

    for letter, accents in ACCENTS.items():
        for accent in accents:
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

    # Replace Satow with Sato
    romaji = regex.sub(r'ow$', 'oh', romaji)

    # Replace shumpei with shunpei
    romaji = regex.sub(r'm(?=[bpm])', 'n', romaji)

    # Replace Itchiku with Icchiku
    romaji = romaji.replace('tch', 'cch')

    # Remove hyphens, sometimes seen in real world data: 'ke-nichiro'
    romaji = regex.sub(r'[-]', '', romaji)

    romaji = romaji.replace('l', 'r')

    # Normalise romaji forms (hu/fu, sya/sha)
    romaji = romkan.to_roma(romkan.to_kana(romaji))

    # Remove apostrophe (used to disambiguate, e.g. 万葉 is man'you,
    # not ma'nyou). We don't care about this because it's unlikely that
    # a name will have two ambiguous kana forms but the same kanji.
    romaji = romaji.replace("'", '')

    # Collapse vowels into one, including 'h' if not followed by a vowel
    # 'hy' is rare (mostly 'hyaku').
    romaji = regex.sub(r'(oh(?![aiueoy])|ou|o+)', 'o', romaji)
    romaji = regex.sub(r'(eh(?![aiueoy])|ei|e+)', 'e', romaji)
    romaji = regex.sub(r'(uh(?![aiueoy])|uu)', 'u', romaji)
    romaji = regex.sub(r'([aiu])\1+', '\\1', romaji)

    # Remove 'h's that are most likely vowels
    romaji = REMOVE_VOWEL_H.get(romaji, romaji)

    return romaji
