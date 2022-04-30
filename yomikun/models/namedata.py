from __future__ import annotations
import dataclasses
import json
import pytest
import regex

from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.lifetime import Lifetime
from yomikun.utils import patterns


def normalise(s: str) -> str:
    """Normalise whitespace in a string"""
    s = s.strip()
    s = regex.sub(r'\s+', ' ', s)
    return s


@dataclasses.dataclass
class NameData:
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
    tags: set[str] = dataclasses.field(default_factory=set)

    # Arbitrary notes. For person records, this indicates the type of person
    # e.g. (actor, musician, politician etc.)
    notes: str = ''

    def __post_init__(self):
        # Do basic type checking, as dataclasses does not
        assert isinstance(self.subreadings, list)

        # Some tests create NameData with tags as a list
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

        self.clean()

    @classmethod
    def person(cls, *args, **kvargs):
        nd = NameData(*args, **kvargs)
        nd.add_tag('person')
        return nd

    def set_name(self, kaki: str, yomi: str):
        self.kaki = kaki
        self.yomi = yomi
        self.clean()
        return self

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
        self.tags.add(tag)
        return self

    def remove_tag(self, tag: str):
        if tag in self.tags:
            self.tags.remove(tag)
        return self

    def remove_tags(self, *tags):
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
        return self

    def has_tag(self, tag: str):
        return tag in self.tags

    def remove_xx_tags(self):
        to_remove = [tag for tag in self.tags if tag.startswith('xx-')]
        for tag in to_remove:
            self.tags.remove(tag)
        return self

    def is_person(self):
        return 'person' in self.tags or (' ' in self.kaki and ' ' in self.yomi)

    def is_given_name(self):
        # Assumes is_person/is_surname already checked.
        return 'masc' in self.tags or 'fem' in self.tags or 'given' in self.tags

    def is_surname(self):
        return 'surname' in self.tags

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

    def set_gender(self, new_gender: str | None):
        self.remove_tags('masc', 'fem')

        if new_gender:
            self.add_tag(new_gender)

        return self

    def clone(self) -> NameData:
        # Use our existing JSONL serialization rather than coding the logic again.
        return NameData.from_jsonl(self.to_jsonl())

    def split(self) -> tuple[NameData, NameData]:
        """
        Split this NameData object into two (surname + given name components).
        This object must be a person with two name parts, and no subreadings,
        otherwise ValueError will be raised.
        """
        if not self.is_person():
            raise ValueError("split(): NameData must be a person")
        if self.subreadings:
            raise ValueError("split(): NameData must not have any subreadings")
        if len(self.kaki.split()) == 1:
            # Even though it's tagged as a person, the kanji is not split into two
            raise ValueError("split(): NameData kaki is not split")

        self.clean_and_validate()

        sei_kaki, mei_kaki = self.kaki.split()
        sei_yomi, mei_yomi = self.yomi.split()

        mei_tag = self.gender() or 'given'

        sei = (
            self.clone()
            .set_name(sei_kaki, sei_yomi)
            .remove_tags('person', 'masc', 'fem', 'given')
            .add_tag('surname')
        )
        mei = (
            self.clone()
            .set_name(mei_kaki, mei_yomi)
            .remove_tags('person', 'given')
            .add_tag(mei_tag)
        )

        return (sei, mei)

    def clean(self):
        """
        Tidy up / normalise all data. Returns self.
        """
        self.kaki = normalise(self.kaki)
        self.yomi = normalise(self.yomi)
        for sub in self.subreadings:
            sub.clean()

        # HACK for Beat Takeshi
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
                    # Was added as a honmyo subreading, which implies it is definitely
                    # the real name.
                    self.authenticity = NameAuthenticity.REAL
                    to_delete += [sub]

        for sub in to_delete:
            self.subreadings.remove(sub)

        return self

    def validate(self):
        """
        Validates the kaki and yomi values are correct based on the tags set.
        Raises ValueError if not correct.
        """
        part = None
        if self.is_person():
            kaki_pat = patterns.name_pat
            if len(self.kaki.split()) == 1:
                yomi_pat = patterns.reading_pat_optional_space
            else:
                yomi_pat = patterns.reading_pat
            part = 'person'
        elif self.is_given_name():
            kaki_pat = patterns.mei_pat
            yomi_pat = patterns.hiragana_pat
            part = 'given'
        elif self.is_surname():
            kaki_pat = patterns.sei_pat
            yomi_pat = patterns.hiragana_pat
            part = 'surname'
        else:
            raise ValueError(
                f'Data should be tagged to indicate part of name: {self.to_jsonl()}'
            )

        if not regex.match(fr'^{kaki_pat}$', self.kaki):
            if self.authenticity == NameAuthenticity.REAL:
                raise ValueError(
                    f"Invalid kaki '{self.kaki}' for part {part} ({self.to_jsonl()})"
                )
            else:
                # Anything is allowed for pen-names and fictional characters
                pass

        if not regex.match(fr'^{yomi_pat}$', self.yomi):
            raise ValueError(
                f"Invalid yomi '{self.yomi}' for part {part} ({self.to_jsonl()})"
            )

        for sub in self.subreadings:
            sub.validate()

    def clean_and_validate(self) -> NameData:
        self.clean()
        self.validate()
        return self

    def to_dict(self) -> dict:
        self.clean()

        # asdict() converts lifetime and subreadings for us. However, it does not call
        # our overriden to_dict (this method) on the subreadings, so we need to do that
        # manually.
        data = dataclasses.asdict(self)

        data['authenticity'] = data['authenticity'].name.lower()

        if data['notes'] == '':
            del data['notes']

        if not self.lifetime:
            del data['lifetime']

        # Use list for tags as JSON has no set operator
        data['tags'] = list(sorted(data['tags']))

        # Does not seem to recurse via asdict()
        if not data['subreadings']:
            del data['subreadings']
        else:
            data['subreadings'] = [x.to_dict() for x in self.subreadings]

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
            data['subreadings'] = list(map(NameData.from_dict, data['subreadings']))
        if 'orig' in data:
            del data['orig']
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = set(data['tags'])

        return NameData(**data)

    @classmethod
    def from_jsonl(cls, jsonl: str) -> NameData:
        return cls.from_dict(json.loads(jsonl))

    def to_csv(self) -> str:
        """
        Returns namedata in custom.csv format
        """
        if self.subreadings:
            raise ValueError('subreadings are not supported with to_csv')

        tags = set(self.tags)
        if 'masc' in tags:
            tags.remove('masc')
            tags.add('m')
        if 'fem' in tags:
            tags.remove('fem')
            tags.add('f')
        if 'surname' in tags:
            tags.remove('surname')
            tags.add('s')

        fields = [self.kaki, self.yomi, '+'.join(tags)]
        lifetime = self.lifetime.to_csv()
        if lifetime or self.notes:
            fields.append(lifetime)
        if self.notes:
            fields.append(self.notes)

        return ','.join(fields)


def test_normalise():
    assert normalise(' foo ') == 'foo'
    assert normalise('A   B') == 'A B'
    assert normalise('亜　美') == '亜 美'


def test_add_tag():
    nd = NameData('高次', 'こうじ')
    nd.add_tag('foo')
    assert nd == NameData('高次', 'こうじ', tags={'foo'})

    nd.add_tag('bar')
    assert nd == NameData('高次', 'こうじ', tags={'foo', 'bar'})


def test_remove_xx():
    nd = NameData(tags={'xx-romaji', 'xx-split', 'foo'})
    nd.remove_xx_tags()
    assert nd.tags == {'foo'}


def test_pos_validation():
    with pytest.raises(ValueError, match=r'^Data should be tagged'):
        NameData('愛', 'あい').validate()

    NameData('愛', 'あい', tags={'fem'}).validate()


def test_kaki_validation():
    nd = NameData.person('梅の里 昭二', 'うめのさと しょうじ')
    with pytest.raises(ValueError, match=r'^Invalid kaki'):
        nd.validate()

    nd.authenticity = NameAuthenticity.PSEUDO
    nd.validate()

    # Allow ノ as it is genuinely seen in names
    NameData.person('木ノ元 明博', 'きのもと あけひろ').validate()


def test_kana_validation():
    nd = NameData('心', 'ココロ', tags={'given'})
    with pytest.raises(ValueError, match=r'^Invalid yomi'):
        nd.validate()


def test_split():
    nd = NameData.person(
        '黒澤 明', 'くろさわ あきら', tags={'xx-romaji', 'masc'}, source='wikipedia_en'
    )
    sei, mei = nd.split()
    assert sei == NameData(
        '黒澤', 'くろさわ', tags={'xx-romaji', 'surname'}, source='wikipedia_en'
    )
    assert mei == NameData(
        '明', 'あきら', tags={'xx-romaji', 'masc'}, source='wikipedia_en'
    )
