import romkan


def romaji_to_hiragana(romaji: str):
    """
    Convert romaji string to hiragana.
    """
    # Convert macrons to long vowels
    romaji = romaji.replace('ō', 'ou')
    romaji = romaji.replace('ā', 'aa')
    romaji = romaji.replace('ē', 'ee')
    return romkan.to_hiragana(romaji)


def test_basic():
    assert romaji_to_hiragana('Sōkokurai Eikichi') == 'そうこくらい えいきち'
