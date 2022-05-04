import regex
from jcconv3 import kata2hira
import pytest

from yomikun.utils.romaji.strict import romaji_to_hiragana_strict


def convert_to_hiragana(yomi: str) -> str:
    """
    Convert katakana or romaji names to hiragana.

    Romaji must be in proper form (雄三 = Yuuzou, not Yuzo) and in
    Western order (GIVEN followed by SURNAME). Case is ignored.
    """
    parts = yomi.split()
    out = []
    formats = set()
    for part in parts:
        if regex.match(r"^[a-z']+$", part, regex.I):
            out.append(romaji_to_hiragana_strict(part))
            formats.add('romaji')
        elif regex.match(r'^\p{Katakana}+$', part):
            out.append(kata2hira(part))
            formats.add('katakana')
        elif regex.match(r'^\p{Hiragana}+$', part):
            out.append(part)
            formats.add('hiragana')
        else:
            raise ValueError(f'Unsupported yomi form "{part}"')

    if len(formats) > 1:
        raise ValueError(f"Inconsistent formats: {', '.join(formats)}")

    if 'romaji' in formats and len(out) > 1:
        # Swap order of romaji names
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
    with pytest.raises(ValueError):
        convert_to_hiragana('123')
