from __future__ import annotations
import dataclasses
import json
import copy

import regex

from yomikun.models.nametype import NameType
from yomikun.models.lifetime import Lifetime


def normalise(s: str) -> str:
    """Normalise whitespace in a string"""
    s = s.strip()
    s = regex.sub(r'\s+', ' ', s)
    return s


@dataclasses.dataclass
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
    lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)

    # Sub-readings (related to this one)
    subreadings: list[NameData] = dataclasses.field(default_factory=list)

    # String identifying the source of this reading
    source: str = ''

    # Arbitrary tags assigned to the name. Used by JMNedict to mark
    # whether a name is a forename or a surname, etc.
    tags: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.clean()

    def add_subreading(self, subreading: NameData):
        """
        Add a subreading.
        """
        self.subreadings.append(subreading)

    def add_tag(self, tag: str):
        self.tags.append(tag)

    def has_name(self) -> bool:
        """
        Returns True if this object has name data fully populated.
        """
        return len(self.kaki) > 0 and len(self.yomi) > 0

    def clean(self):
        """
        Tidy up / normalise all data.
        """
        self.kaki = normalise(self.kaki)
        self.yomi = normalise(self.yomi)
        for sub in self.subreadings:
            sub.clean()

    def to_dict(self) -> dict:
        self.clean()
        data = dataclasses.asdict(self)
        data['name_type'] = data['name_type'].name.lower()
        data['lifetime'] = data['lifetime'].to_dict()
        data['subreadings'] = map(lambda x: x.to_dict(), data['subreadings'])

        return data

    def to_jsonl(self) -> str:
        """
        Converts a NameData to a JSONL string.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @ classmethod
    def from_dict(cls, data: dict) -> NameData:
        if 'name_type' in data:
            data['name_type'] = NameType[data['name_type'].upper()]
        if 'lifetime' in data:
            data['lifetime'] = Lifetime(**data['lifetime'])
        if 'subreadings' in data:
            data['subreadings'] = map(
                lambda x: NameData.from_dict(x), data['subreadings'])
        return NameData(**data)

    @ classmethod
    def merge(cls, a: NameData, b: NameData) -> NameData:
        """
        Merge two NameData records. The records should correspond to the
        same person!
        """
        # Normalise the values of both records
        a.clean()
        b.clean()

        if b.has_name():
            a, b = b, a

        merged = copy.deepcopy(a)

        merged.lifetime.merge_in(b.lifetime)
        merged.subreadings += b.subreadings

        return merged


def test_normalise():
    assert normalise(' foo ') == 'foo'
    assert normalise('A   B') == 'A B'
    assert normalise('亜　美') == '亜 美'
