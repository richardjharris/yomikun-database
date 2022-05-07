import dataclasses
from dataclasses import dataclass

import regex

from yomikun.utils import patterns


@dataclass
class ResearchMapRecord:
    """
    Holds a single row from the research map input data.
    """

    kana: str
    kanji: str
    english: str

    def has_name_kanji(self) -> bool:
        """
        Returns true if this record's `kanji` field looks like a name.
        """
        return regex.fullmatch(patterns.name_pat, self.kanji) is not None

    def has_romaji(self) -> bool:
        """
        Returns true if this record's `english` or `kana` fields contain
        romaji.
        """
        return regex.search('[a-z]', self.kana + self.english) is not None

    def stripped(self):
        """
        Returns a copy with all fields stripped of surrounding whitespace.
        """
        return ResearchMapRecord(
            kana=self.kana.strip(),
            kanji=self.kanji.strip(),
            english=self.english.strip(),
        )

    def astuple(self):
        return dataclasses.astuple(self)

    def clone(self):
        return dataclasses.replace(self)

    def __str__(self):
        return str(self.astuple())
