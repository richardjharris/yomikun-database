from dataclasses import dataclass

from yomikun.models.nameposition import NamePosition


@dataclass(frozen=True)
class NamePart:
    kaki: str
    yomi: str
    position: NamePosition
