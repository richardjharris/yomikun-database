from __future__ import annotations
from dataclasses import dataclass, field
import json

import regex
from dataclasses_json import dataclass_json

from models.nametype import NameType
from models.lifetime import Lifetime


def normalise(s: str) -> str:
    """Normalise whitespace in a string"""
    s = s.strip()
    s = regex.sub(r'\s+', '', s)
    return s


@dataclass_json
@dataclass
class NameData():
    """
    Name data extracted by the parsers.
    """
    # Full name (parts separated by a space)
    kaki: str = ''
    yomi: str = ''

    # Reading type
    name_type: NameType = NameType.REAL

    # Years lived for this name
    lifetime: Lifetime = field(default_factory=Lifetime)

    # Sub-readings (related to this one)
    subreadings: list[NameData] = field(default_factory=list)

    def __post_init__(self):
        # TODO normalise in setter also
        self.kaki = normalise(self.kaki)
        self.yomi = normalise(self.yomi)

    def add_subreading(self, subreading: NameData):
        """
        Add a subreading.
        """
        self.subreadings.append(subreading)

    def has_name(self) -> bool:
        """
        Returns True if this object has name data populated.
        """
        return len(self.kaki) > 0 or len(self.yomi) > 0

    def __str__(self) -> str:
        """
        Converts the NameData to a short, human-readable YAML style
        string.
        """
        desc = f"name: {self.kaki} ({self.yomi})\n"
        desc += f"type: {self.name_type}\n"
        if self.lifetime:
            desc += f"lifetime: {self.lifetime}\n"
        if self.subreadings:
            desc += f"subreadings:\n"
            for sub in self.subreadings:
                subdesc = str(sub)
                subdesc = ''.join('  ' + line for line in subdesc.splitlines())
                subdesc = subdesc.replace('  ', '- ', 1)
                desc += subdesc
        return desc

    def to_jsonl(self) -> str:
        """
        Converts a NameData to a JSONL string.
        """
        # TODO consider existing dataclasses.asdict() func
        return json.dumps(self.to_dict(), ensure_ascii=False)  # type: ignore
