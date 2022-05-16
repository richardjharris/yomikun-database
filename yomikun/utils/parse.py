from yomikun.models.namedata import NameData
from yomikun.researchmap.parser import _parse_researchmap_inner
from yomikun.researchmap.record import ResearchMapRecord


def parse_romaji_name(romaji: str, kanji: str) -> NameData | None:
    """
    Parse a romaji full name with kanji and return NameData.

    Converts romaji to hiragana intelligently using kanji for reference, e.g.
    it knows that ('ono', '大野') is mostly likely おおの.

    Assumes the romaji is LASTNAME firstname format, but swaps them if the
    swapped version seems more likely based on the kanji.

    Returns None if parsing is not possible.
    """
    record = ResearchMapRecord(romaji, kanji, '')
    namedata = _parse_researchmap_inner(record, swap_names=True)
    return namedata
