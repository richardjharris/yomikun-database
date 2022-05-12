from __future__ import annotations

import copy
import dataclasses
import json
from dataclasses import dataclass, field

import regex

from yomikun.models.gender import Gender
from yomikun.models.lifetime import Lifetime
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namepart import NamePart
from yomikun.models.nameposition import NamePosition
from yomikun.utils import normalise_whitespace, patterns
from yomikun.utils.convert import convert_to_hiragana


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
    Tags associated with the name.

    The gender and type of a name is indicated by a tag combination:

      masc: male given
      fem: female given
      given: given (no gender)
      surname: surname
      masc, person: male person
      fem, person: female person
      person: person (no gender)

    Additional tags include 'dict' (not a real-world sighting of the name).
    """
    # Arbitrary tags assigned to the name. Used by JMNedict to mark
    # whether a name is a forename or a surname, etc.
    tags: set[str] = field(default_factory=set)

    # Arbitrary notes. For person records, this indicates the type of person
    # e.g. (actor, musician, politician etc.)
    notes: str = ''

    def __post_init__(self):
        # Do basic type checking, as selfclasses does not
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
        Returns True if this object has name self fully populated.
        """
        return len(self.kaki) > 0 and len(self.yomi) > 0

    def gender(self) -> str | None:
        if 'fem' in self.tags:
            return 'fem'
        elif 'masc' in self.tags:
            return 'masc'
        else:
            return None

    def _gender_typed(self) -> Gender:
        tags = self.tags
        if 'masc' in tags and 'fem' in tags:
            return Gender.neutral
        elif 'masc' in tags:
            return Gender.male
        elif 'fem' in tags:
            return Gender.female
        else:
            return Gender.unknown

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

    def extract_name_parts(self) -> list[tuple[NamePart, Gender | None]]:
        """
        Used by RomajiDB, GenderDB, person dedupe etc.

        Return a list of name parts from this NameData record. If this record is
        a person, outputs a sei and mei record; otherwise, outputs a single record
        matching this name's position.
        """
        self.clean()

        parts = []
        if self.is_person():
            # Sometimes is tagged [person, fem] to indicate the person's gender.
            gender = self._gender_typed()
            kakis = self.kaki.split()
            yomis = self.yomi.split()
            if len(kakis) == 2 and len(yomis) == 2:
                sei = NamePart(kaki=kakis[0], yomi=yomis[0], position=NamePosition.sei)
                mei = NamePart(kaki=kakis[1], yomi=yomis[1], position=NamePosition.mei)
                parts += [(sei, gender), (mei, gender)]
            else:
                # Can't reliably assign positions to names
                part = NamePart(
                    kaki=self.kaki, yomi=self.yomi, position=NamePosition.unknown
                )
                parts.append((part, gender))
        elif 'unclass' in self.tags:
            for tag in ('person', 'surname', 'given', 'fem', 'masc'):
                assert not self.has_tag(tag)

            part = NamePart(
                kaki=self.kaki, yomi=self.yomi, position=NamePosition.unknown
            )
            parts.append((part, None))
        else:
            # Names may be a combination of masc,fem,given,surname
            if 'surname' in self.tags:
                sei = NamePart(
                    kaki=self.kaki, yomi=self.yomi, position=NamePosition.sei
                )
                parts.append((sei, None))
            elif set(self.tags).intersection({'masc', 'fem', 'given'}):
                gender = self._gender_typed()
                mei = NamePart(
                    kaki=self.kaki, yomi=self.yomi, position=NamePosition.mei
                )
                parts.append((mei, gender))

        return parts

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
        Returns name data in custom.csv format
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
        if self.authenticity == NameAuthenticity.PSEUDO:
            tags.add('pseudo')
        if self.authenticity == NameAuthenticity.FICTIONAL:
            tags.add('fictional')

        fields = [self.kaki, self.yomi, '+'.join(sorted(tags))]
        lifetime = self.lifetime.to_csv()
        if lifetime or self.notes:
            fields.append(lifetime)
        if self.notes:
            fields.append(self.notes)

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
        namedata = NameData(kaki, yomi)

        if row['tags']:
            tags = row['tags'].split('+')
            for tag in tags:
                if tag == 'm':
                    namedata.set_gender('masc')
                elif tag == 'f':
                    namedata.set_gender('fem')
                elif tag == 's':
                    namedata.set_gender('surname')
                elif tag == 'pseudo':
                    namedata.authenticity = NameAuthenticity.PSEUDO
                elif tag in ('fictional', 'fict'):
                    namedata.authenticity = NameAuthenticity.FICTIONAL
                else:
                    namedata.add_tag(tag)

        if namedata.is_person():
            namedata.add_tag('person')

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
