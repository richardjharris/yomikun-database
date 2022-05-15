import pytest
import regex
import romkan


def romaji_to_hiragana_strict(romaji: str) -> str:
    """
    Converts romaji to hiragana strictly, i.e. it is assumed that the romaji
    will correctly use long and short vowels to match the kana equivalent,
    apostrophes if needed, and no macrons.

    Returns the hiragana form of the name.
    """
    romaji = romaji.lower()
    if not regex.search(r"^[a-z' ]*$", romaji):
        raise ValueError(f"Input '{romaji}' has weird characters in it. Yuk!")

    # Fix 'Itchiku' (いっちく、一竹)
    romaji = romaji.replace("tch", "cch")

    return romkan.to_hiragana(romaji)


def test_romaji_to_hiragana_strict():
    assert romaji_to_hiragana_strict("shinjiro") == "しんじろ"
    assert romaji_to_hiragana_strict("AKEMI") == "あけみ"
    assert romaji_to_hiragana_strict("ITCHIKU") == "いっちく"
    assert romaji_to_hiragana_strict('') == ""

    with pytest.raises(ValueError):
        romaji_to_hiragana_strict("123")
