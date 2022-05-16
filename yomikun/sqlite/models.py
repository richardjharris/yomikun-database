# Mapping of namedata part names to their IDs. This is done as SQLite
# does not support enums.
from __future__ import annotations

from enum import Enum

from yomikun.models.name_position import NamePosition


# TODO: remove duplication between NamePart and NamePosition
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

    @classmethod
    def from_position(cls, position: NamePosition) -> NamePart:
        match (position):
            case NamePosition.sei:
                return NamePart.sei
            case NamePosition.mei:
                return NamePart.mei
            case NamePosition.person:
                return NamePart.person
            case NamePosition.unknown:
                return NamePart.unknown

        assert False
