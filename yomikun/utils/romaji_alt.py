"""
Alternate romaji matching code - not currently needed as
the romaji_key thing is good enough, but may be needed later.
"""
from operator import itemgetter
import functools
import unicodedata

import pytest
import regex


@functools.cache
def romaji_to_pattern(romaji: str) -> regex.Pattern:
    """
    Converts a string such as Goto to a pattern that can match ごと、ごとう、
    ごうと and ごうとう i.e. /go[ou]?to[ou]?/ to handle ambiguous romaji.
    The patterns are intended to match against the output of
    `romkan.to_roma`:
      こんにちは -> kon'nichiha　　　んあ -> n'a　　　　ぢ -> di
      しゃ -> sha　　おおおう -> ooou  つづく -> tsuduku  おをお -> owoo
      うぃ -> uxi　ふ -> fu

    To deal with arbitrary input might be harder? Ohsuke etc.

    If the string contains at least one macron(e.g. 'Ō'), assumes all
    vowels are properly marked with macrons.

    TODO: Tôkyô
    TODO: how to handle Tokyou (where u could actually be o, or both?)
    """
    romaji = romaji.lower()
    # Recompose macrons
    romaji = unicodedata.normalize('NFC', romaji)

    has_macron = regex.match('[ōāēū]', romaji)

    parts = regex.split(r"""
        (?:
        # apostrophe split e.g. kon'nyaku
         '
        |
        # non-vowel + vowel + optional h (if not followed by a vowel)
        # e.g. 'ohtani' -> oh|ta|ni but 'ohare' -> o|ha|re
         (?<= [^aiueo]* [aiueo] (?: h(?![aiueo]) )? )
        )
    """, romaji, flags=regex.VERBOSE)
    pattern = ''
    print(parts)

    for part in parts:
        if not part:
            continue

        # A trailing 'h' can be ignored as we always extend vowels
        if part.endswith('h'):
            part = part[0:-2]

        if part.endswith('o'):
            # ko
            pass

    return regex.compile(pattern)


rtp_tests = [
    ('koutou', 'koutou'),  # already expanded
    ('goto', 'g[ou]?t[ou]?'),
    ('yusuke', 'yuu?suu?ke[ei]?'),
    ('ohtani', 'o[ou]tani'),
    ('Ohare', 'o[ou]?hare[ei]?'),
    ('tokyo', 'to[ou]?kyo[ou]?'),
    ('Tōkyō', 'to[ou]ky[ou]'),
]


@pytest.mark.skip
@pytest.mark.parametrize('test', rtp_tests, ids=itemgetter(0))
def test_romaji_to_pattern(test):
    romaji, expected = test
    result = romaji_to_pattern(romaji)
    assert result.pattern == result
