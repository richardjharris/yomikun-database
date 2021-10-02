from audioop import reverse
import regex
from jcconv3 import kata2hira
import pytest

from yomikun.utils.romaji import romaji_to_hiragana


def convert_to_hiragana(yomi: str) -> str:
    """
    Convert katakana or romaji names to hiragana.
    """
    parts = yomi.split()
    out = []
    romaji = None
    for part in parts:
        if regex.match(r'^[a-z]+$', part, regex.I):
            if romaji == False:
                raise ValueError('mix of romaji and non-romaji')
            out.append(romaji_to_hiragana(part))
            romaji = True
        elif regex.match(r'^\p{Furigana}+$', part):
            out.append(kata2hira(part))
        elif regex.match(r'^\p{Hiragana}+$', part):
            out.append(part)
        else:
            raise ValueError(f'Unsupported yomi form "{part}"')

    if romaji and len(out) > 1:
        # Romaji names are assumed to be in reverse order
        assert len(out) == 2
        out.reverse()

    return ' '.join(out)


def test_convert_to_hiragana():
    assert convert_to_hiragana('Suzuki Hirabe') == 'ひらべ すずき'
    assert convert_to_hiragana('Yuuzou　Kouda') == 'こうだ ゆうぞう'
    assert convert_to_hiragana('フジモト　ミキ') == 'ふじもと みき'
    assert convert_to_hiragana('みき') == 'みき'
    assert convert_to_hiragana('みき ゆ') == 'みき ゆ'
    assert convert_to_hiragana('みき 　　　　　　ゆ') == 'みき ゆ'
    assert convert_to_hiragana('Naoki') == 'なおき'
    with pytest.raises(ValueError):
        convert_to_hiragana('Naoki ふじもと')
