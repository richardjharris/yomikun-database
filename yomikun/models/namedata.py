from __future__ import annotations
import dataclasses
import json
import copy

import regex

from yomikun.models.nameauthenticity import NameAuthenticity
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
    authenticity: NameAuthenticity = NameAuthenticity.REAL

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
        # Do basic type checking, as dataclasses does not
        assert isinstance(self.subreadings, list)
        self.clean()

    def add_subreading(self, subreading: NameData):
        """
        Add a subreading.
        """
        self.subreadings.append(subreading)

    def add_honmyo(self, honmyo: NameData):
        assert honmyo.authenticity == NameAuthenticity.REAL
        self.authenticity = NameAuthenticity.PSEUDO
        self.add_subreading(honmyo)

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def is_person(self):
        return 'person' in self.tags or (' ' in self.kaki and ' ' in self.yomi)

    def has_name(self) -> bool:
        """
        Returns True if this object has name data fully populated.
        """
        return len(self.kaki) > 0 and len(self.yomi) > 0

    def gender(self) -> str | None:
        if 'fem' in self.tags:
            return 'fem'
        elif 'masc' in self.tags:
            return 'masc'
        else:
            return None

    def set_gender(self, new_gender: str):
        if 'masc' in self.tags:
            self.tags.remove('masc')
        if 'fem' in self.tags:
            self.tags.remove('fem')

        self.tags.append(new_gender)

    def clone(self) -> NameData:
        # Use our existing JSONL serialization rather than coding the logic again.
        return NameData.from_jsonl(self.to_jsonl())

    def clean(self):
        """
        Tidy up / normalise all data. Returns self.
        """
        self.kaki = normalise(self.kaki)
        self.yomi = normalise(self.yomi)
        for sub in self.subreadings:
            sub.clean()

        ### BEAT TAKESHI HACK ###
        to_delete = []
        for sub in self.subreadings:
            if (self.kaki, self.yomi) == (sub.kaki, sub.yomi):
                # Delete the subreading. One example case is beat takeshi which has two
                # infoboxes:
                # 1) name = ビートたけし, 本名 = 北野 武（きたの たけし）
                # 2) name = 北野 武（きたの たけし）
                # This creates 北野 武 (pseudo) -> 北野 武 (real) because both infoboxes
                # are parsed together. An 'unknown' authenticity that gets resolved to
                # 'real' later could help here. and/or parsing the boxes seperately...
                if sub.authenticity == NameAuthenticity.REAL:
                    # Was added as a honmyo subreading, which implies it is definitely the
                    # real name.
                    self.authenticity = NameAuthenticity.REAL
                    to_delete += [sub]

        for sub in to_delete:
            self.subreadings.remove(sub)

        return self

    def to_dict(self) -> dict:
        self.clean()

        # asdict() converts lifetime and subreadings for us. However, it does not call
        # our overriden to_dict (this method) on the subreadings, so we need to do that
        # manually.
        # TODO we could use __dict__ directly instead.
        data = dataclasses.asdict(self)

        data['authenticity'] = data['authenticity'].name.lower()
        for subreading in data['subreadings']:
            subreading['authenticity'] = subreading['authenticity'].name.lower()

        return data

    def to_jsonl(self) -> str:
        """
        Converts a NameData to a JSONL string.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> NameData:
        if 'authenticity' in data:
            data['authenticity'] = NameAuthenticity[data['authenticity'].upper()]
        if 'lifetime' in data:
            data['lifetime'] = Lifetime(**data['lifetime'])
        if 'subreadings' in data:
            data['subreadings'] = list(map(
                lambda x: NameData.from_dict(x), data['subreadings']))
        if 'orig' in data:
            del data['orig']
        return NameData(**data)

    @classmethod
    def from_jsonl(cls, jsonl: str) -> NameData:
        return cls.from_dict(json.loads(jsonl))


def test_normalise():
    assert normalise(' foo ') == 'foo'
    assert normalise('A   B') == 'A B'
    assert normalise('亜　美') == '亜 美'
