from __future__ import annotations

import copy
import dataclasses
import json
import logging
from dataclasses import dataclass, field

import regex

from yomikun.models.gender import Gender
from yomikun.models.lifetime import Lifetime
from yomikun.models.name_authenticity import NameAuthenticity
from yomikun.models.name_position import NamePosition
from yomikun.utils import normalise_whitespace, patterns
from yomikun.utils.convert import convert_to_hiragana


@dataclass(frozen=True)
class NameDataKey:
    kaki: str
    yomi: str
    position: NamePosition


@dataclass
class NameData:
    """
    Name data extracted by the parsers.

    NameData records can represent either a person's full name, or part
    of a name. In the former case, `kaki` and `yomi` will both contain
    a space. To identify what kind of name is represented, the `tags`
    field is used.
    """

    """Written form of name (typically kanji)"""
    kaki: str = ''

    """Reading form of name (hiragana)"""
    yomi: str = ''

    """
    Whether the name is real, a pen-name or fictional.

    This is used in the Yomikun app to inform the user that particular
    names may not actually be used in the real world, only in fiction.
    """
    authenticity: NameAuthenticity = NameAuthenticity.REAL

    """
    Gender of name, if a given name or person
    """
    gender: Gender = Gender.unknown

    """
    Type of name this record represents.
    """
    position: NamePosition = NamePosition.unknown

    """
    Life span of this name.

    This is used in aggregate to indicate that certain names are
    particularly new or particularly old, and also as a way of de-duplicating
    person records across multiple sources.
    """
    lifetime: Lifetime = field(default_factory=Lifetime)

    """
    Subreadings attached to this name.

    This is used as a convenient way for NameData parsers to return multiple
    readings (typically a pen-name or pseudonym) along with the main reading.

    Subreadings are assumed to all represent the same person.
    """
    subreadings: list[NameData] = field(default_factory=list)

    """
    String identifying the source of this name.

    By convention, this is the JSONL filename (e.g. 'pdd') with an optional
    article or heading name after a colon (e.g. 'wikipedia_en:Masamune_Shirow')
    """
    source: str = ''

    """
    True if this name represents a dictionary entry. Such names do not contribute
    to a name hit count, and are included for completeness.
    """
    is_dict: bool = False

    # Arbitrary tags assigned to the name. (Legacy)
    tags: set[str] = field(default_factory=set)

    # Arbitrary notes. For person records, this indicates the type of person
    # e.g. (actor, musician, politician etc.)
    notes: str = ''

    def key(self) -> NameDataKey:
        """
        Key used for name equality: kaki, yomi and position.

        This is the most typical way to dedupe or aggregate names, and also the
        primary key in the SQLite database.
        """
        return NameDataKey(self.kaki, self.yomi, self.position)

    def __post_init__(self):
        # Do basic type checking, as selfclasses does not
        assert isinstance(self.subreadings, list)

        # Some tests create NameData with tags as a list
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

        # Handle legacy tags
        # FIXME: remove
        if self.tags:
            if 'person' in self.tags or (' ' in self.kaki or ' ' in self.yomi):
                self.position = NamePosition.person
            elif 'surname' in self.tags:
                self.position = NamePosition.sei
            elif self.tags & {'given', 'masc', 'fem'}:
                self.position = NamePosition.mei

            if 'fem' in self.tags:
                self.gender = Gender.female
            elif 'masc' in self.tags:
                self.gender = Gender.male

            if 'dict' in self.tags:
                self.is_dict = True

            # Remove the tags we have handled
            self.tags -= {'person', 'surname', 'given', 'masc', 'fem', 'dict'}
            # FIXME: complain if any tags are not xx-*

        self.clean()

    @classmethod
    def person(cls, *args, **kvargs):
        return NameData(*args, **kvargs, position=NamePosition.person)

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

    def remove_xx_tags(self):
        to_remove = [tag for tag in self.tags if tag.startswith('xx-')]
        for tag in to_remove:
            self.tags.remove(tag)
        return self

    def has_name(self) -> bool:
        """
        Returns True if this object has name self fully populated.
        """
        return len(self.kaki) > 0 and len(self.yomi) > 0

    def clone(self) -> NameData:
        # Use our existing JSONL serialization rather than coding the logic again.
        return NameData.from_jsonl(self.to_jsonl())

    def split(self, ignore_subreadings=False) -> tuple[NameData, NameData]:
        """
        Split this NameData object into two (surname + given name components).
        This object must be a person with two name parts, and no subreadings,
        otherwise ValueError will be raised.
        """
        if self.position != NamePosition.person:
            raise ValueError("split(): NameData must be a person")
        if self.subreadings and not ignore_subreadings:
            raise ValueError("split(): NameData must not have any subreadings")
        if len(self.kaki.split()) == 1:
            # Even though it's tagged as a person, the kanji is not split into two
            raise ValueError("split(): NameData kaki is not split")

        self.clean()

        sei_kaki, mei_kaki = self.kaki.split()
        sei_yomi, mei_yomi = self.yomi.split()

        sei = self.clone().set_name(sei_kaki, sei_yomi)
        sei.position = NamePosition.sei
        sei.gender = Gender.unknown

        mei = self.clone().set_name(mei_kaki, mei_yomi)
        mei.position = NamePosition.mei

        return (sei, mei)

    def extract_name_parts(self) -> list[NameData]:
        """
        Used by RomajiDB, GenderDB, person dedupe etc.

        Return a list of name parts from this NameData record. If this record is
        a person, outputs a sei and mei record; otherwise, outputs the record
        as-is.
        """
        self.clean()

        names = []
        if (
            self.position == NamePosition.person
            and len(self.kaki.split()) == 2
            and len(self.yomi.split()) == 2
        ):
            names += self.split(ignore_subreadings=True)
        else:
            names += [self]

        for subreading in self.subreadings:
            names += subreading.extract_name_parts()

        return names

    def clean(self):
        """
        Tidy up / normalise all data. Returns self.
        """
        self.kaki = normalise_whitespace(self.kaki)
        self.yomi = normalise_whitespace(self.yomi)
        for sub in self.subreadings:
            sub.clean()

        # HACK: for Beat Takeshi
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

        self._copy_pseudo_data_to_subreadings()

        return self

    def _copy_pseudo_data_to_subreadings(self):
        """
        Copy information in the main (pseudo) NameData reading to any real
        subreadings, including lifetime, source, tags.

        Does nothing if the main reading is not PSEUDO.
        """
        # FIXME: copies 'xx-romaji' too which is wrong
        for subreading in self.subreadings:
            # Copy over the lifetime / gender / source to the real actor
            if (
                self.authenticity == NameAuthenticity.PSEUDO
                and subreading.authenticity == NameAuthenticity.REAL
            ):
                if self.lifetime and not subreading.lifetime:
                    subreading.lifetime = copy.copy(self.lifetime)
                if self.source and not subreading.source:
                    subreading.source = self.source
                if self.tags and not subreading.tags:
                    subreading.tags = self.tags

                subreading.gender = self.gender

    def validate(self):
        """
        Validates the kaki and yomi values are correct based on the name type.

        Raises ValueError if not correct.
        """
        match self.position:
            case NamePosition.person:
                kaki_pat = patterns.name_pat
                if len(self.kaki.split()) == 1:
                    yomi_pat = patterns.reading_pat_optional_space
                else:
                    yomi_pat = patterns.reading_pat
            case NamePosition.mei:
                kaki_pat = patterns.mei_pat
                yomi_pat = patterns.hiragana_pat
            case NamePosition.sei:
                kaki_pat = patterns.sei_pat
                yomi_pat = patterns.hiragana_pat
            case NamePosition.unknown:
                logging.error(self)
                raise ValueError("name with position=unknown")

        if not regex.search(fr'^{kaki_pat}$', self.kaki):
            if self.authenticity == NameAuthenticity.REAL:
                raise ValueError(
                    f"Invalid kaki '{self.kaki}' for part {self.position} ({self.to_jsonl()})"
                )
            else:
                # Anything is allowed for pen-names and fictional characters
                pass

        if not regex.search(fr'^{yomi_pat}$', self.yomi):
            raise ValueError(
                f"Invalid yomi '{self.yomi}' for part {self.position} ({self.to_jsonl()})"
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
        data['gender'] = data['gender'].name.lower()
        data['position'] = data['position'].name.lower()

        if data['notes'] == '':
            del data['notes']

        if not self.lifetime:
            del data['lifetime']

        if self.gender == Gender.unknown:
            del data['gender']

        if self.position == NamePosition.unknown:
            del data['position']

        # Use list for tags as JSON has no set operator
        data['tags'] = list(sorted(data['tags']))
        if not data['tags']:
            del data['tags']

        if not data['is_dict']:
            del data['is_dict']

        # Does not seem to recurse via asdict()
        if not data['subreadings']:
            del data['subreadings']
        else:
            data['subreadings'] = [x.to_dict() for x in self.subreadings]

        return data

    # --------------------------------------------------------------------------------
    # Conversion methods (JSON/CSV)
    # --------------------------------------------------------------------------------

    def to_jsonl(self) -> str:
        """
        Converts a NameData to a JSONL string.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> NameData:
        if 'authenticity' in data:
            data['authenticity'] = NameAuthenticity[data['authenticity'].upper()]
        if 'gender' in data:
            data['gender'] = Gender[data['gender'].lower()]
        if 'position' in data:
            data['position'] = NamePosition[data['position'].lower()]
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

    # FIXME: handle new fields
    def to_csv(self) -> str:
        """
        Returns name data in custom.csv format
        """
        if self.subreadings:
            raise ValueError('subreadings are not supported with to_csv')

        tags = set(self.tags)
        if self.gender == Gender.male:
            tags.add('m')
        elif self.gender == Gender.female:
            tags.add('f')

        if self.position == NamePosition.sei:
            tags.add('s')

        if self.authenticity == NameAuthenticity.PSEUDO:
            tags.add('pseudo')
        if self.authenticity == NameAuthenticity.FICTIONAL:
            tags.add('fictional')

        tags_joined = '+'.join(sorted(tags))

        fields = [self.kaki, self.yomi, tags_joined, self.lifetime.to_csv(), self.notes]

        # Remove trailing empty fields
        while fields and fields[-1] == '':
            fields.pop()

        return ','.join(fields)

    @classmethod
    def from_csv(cls, row: dict) -> NameData:
        """
        Parse an incoming CSV data row and return a NameData object.

        Row must a parsed dict containing the fields: kaki, yomi,
        tags, lifetime, notes.
        """
        kaki = row['kaki']
        yomi = convert_to_hiragana(row['yomi'])
        namedata = NameData(kaki, yomi, position=NamePosition.mei)

        if row['tags']:
            tags = row['tags'].split('+')
            for tag in tags:
                if tag == 'm':
                    namedata.gender = Gender.male
                elif tag == 'f':
                    namedata.gender = Gender.female
                elif tag == 's':
                    namedata.position = NamePosition.sei
                elif tag == 'pseudo':
                    namedata.authenticity = NameAuthenticity.PSEUDO
                elif tag in ('fictional', 'fict'):
                    namedata.authenticity = NameAuthenticity.FICTIONAL
                else:
                    namedata.tags.add(tag)

        # Assume person if the name contained spaces
        if len(kaki.split()) == 2:
            namedata.position = NamePosition.person

        if row['lifetime']:
            try:
                birth, death = row['lifetime'].split('-')
            except ValueError:
                birth = row['lifetime']
                death = ''

            if len(birth):
                namedata.lifetime.birth_year = int(birth)
            if len(death):
                namedata.lifetime.death_year = int(death)

        if row['notes']:
            namedata.notes = row['notes']

        # Normalise spaces
        namedata.clean()
        return namedata
