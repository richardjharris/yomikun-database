import functools

import unicodedata
import romkan
import regex

# Romaji keys where the 'h' is part of the vowel and should
# be removed, e.g. 'ohishi' (おおいし) vs. 'ohashi' (おおはし)
remove_vowel_h = {
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

    # Replace Satow with Sato
    romaji = regex.sub(r'ow$', 'oh', romaji)

    # Replace shumpei with shunpei
    romaji = regex.sub(r'm(?=[bpm])', 'n', romaji)

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
    # TODO: we could ignore 'y', 'hya' is very rare in names and always
    #       always 'hyak-' if present
    romaji = regex.sub(r'(oh(?![aiueoy])|ou|o+)', 'o', romaji)
    romaji = regex.sub(r'(eh(?![aiueoy])|ei|e+)', 'e', romaji)
    romaji = regex.sub(r'(uh(?![aiueoy])|uu)', 'u', romaji)
    romaji = regex.sub(r'([aiu])\1+', '\\1', romaji)

    # Remove 'h's that are most likely vowels
    romaji = remove_vowel_h.get(romaji, romaji)

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
    assert romaji_key('satow') == romaji_key('satou')
    assert romaji_key('shumpei') == romaji_key('shunpei')


def test_romaji_key_m():
    assert romaji_key('shimba') == romaji_key('shinba')
    assert romaji_key('homma') == romaji_key('honma')


def test_romaji_key_punct():
    assert romaji_key('tomo-o') == romaji_key('tomo')
    assert romaji_key("ken'ichi") == romaji_key('kenichi')


def test_romaji_key_h():
    assert romaji_key('kumanogoh') == romaji_key('kumanogou')
    assert romaji_key('kumanogou') == romaji_key('kumanogo')
    assert romaji_key('yuhsuke') == romaji_key('yuusuke')


def test_romaji_key_h_vowel():
    assert romaji_key('ohishi') == romaji_key('oishi')
    assert romaji_key('ohiwa') == romaji_key('oiwa')
    assert romaji_key('ohoka') == romaji_key('oooka')
    assert romaji_key('ohoka') == romaji_key('ōoka')
    assert romaji_key('ohori') == romaji_key('oori')
