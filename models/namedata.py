from __future__ import annotations
from dataclasses import dataclass, field
import json
import copy

import regex
from dataclasses_json import DataClassJsonMixin

from models.nametype import NameType
from models.lifetime import Lifetime


def normalise(s: str) -> str:
    """Normalise whitespace in a string"""
    s = s.strip()
    s = regex.sub(r'\s+', ' ', s)
    return s


@dataclass
class NameData(DataClassJsonMixin):
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
        self.clean()

    def add_subreading(self, subreading: NameData):
        """
        Add a subreading.
        """
        self.subreadings.append(subreading)

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

    def to_jsonl(self) -> str:
        """
        Converts a NameData to a JSONL string.
        """
        self.clean()
        # TODO consider existing dataclasses.asdict() func
        return json.dumps(self.to_dict(),
                          ensure_ascii=False,
                          default=lambda x: x.name.lower(),
                          )

    @ classmethod
    def relaxed_merge(cls, a: NameData | None, b: NameData | None):
        """
        Merge two NameData records, treating None as an empty record.
        """
        # TODO it's ugly how we use None for empty data here, we may
        # want to always return NameData.
        if a is None:
            return b
        elif b is None:
            return a
        else:
            return cls.merge(a, b)

    @ classmethod
    def merge(cls, a: NameData, b: NameData) -> NameData:
        """
        Merge two NameData records. The records must correspond to the
        same person in the same context (real/pseudo/pen-name).
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
