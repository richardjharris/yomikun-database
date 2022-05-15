# Mapping of namedata part names to their IDs. This is done as SQLite
# does not support enums.
from enum import Enum


class NamePart(Enum):
    """Represents the position of a name."""

    unknown = 0
    sei = 1
    mei = 2
    person = 3

    @property
    def kanji(self) -> str:
        match (self):
            case self.unknown:
                return "？"
            case self.sei:
                return "姓"
            case self.mei:
                return "名"
            case self.person:
                return "人"

        assert False
