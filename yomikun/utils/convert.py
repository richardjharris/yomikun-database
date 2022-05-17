import jcconv3
import pytest
import regex

from yomikun.utils.romaji.strict import romaji_to_hiragana_strict


def convert_to_hiragana(yomi: str, swap_names: bool = True) -> str:
    """
    Convert katakana or romaji names to hiragana.

    Romaji must be in proper form (雄三 = Yuuzou, not Yuzo) and in
    Western order (GIVEN followed by SURNAME). Case is ignored.
    """
    parts = yomi.split()
    out = []
    formats = set()
    for part in parts:
        if regex.search(r"^[a-z']+$", part, regex.I):
            out.append(romaji_to_hiragana_strict(part))
            formats.add('romaji')
        elif regex.search(r'^\p{Katakana}+$', part):
            out.append(jcconv3.kata2hira(part))
            formats.add('katakana')
        elif regex.search(r'^\p{Hiragana}+$', part):
            out.append(part)
            formats.add('hiragana')
        else:
            raise ValueError(f'Unsupported yomi form "{part}"')

    if len(formats) > 1:
        raise ValueError(f"Inconsistent formats: {', '.join(formats)}")

    if swap_names and 'romaji' in formats and len(out) > 1:
        # Swap order of romaji names
        assert len(out) == 2
        out.reverse()

    return ' '.join(out)


def test_convert_to_hiragana():
    assert convert_to_hiragana('Suzuki Hirabe') == 'ひらべ すずき'
    assert convert_to_hiragana('Suzuki Hirabe', swap_names=False) == 'すずき ひらべ'
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
