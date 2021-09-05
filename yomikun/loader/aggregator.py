from __future__ import annotations
import copy
from dataclasses import dataclass

import yomikun.models
from yomikun.models import NameData
from yomikun.loader.models import Gender, Person, Name, Base, NameType


@dataclass(frozen=True)
class NamePart:
    kaki: str
    yomi: str
    name_type: NameType


class Aggregator():
    def __init__(self):
        self._people = []
        self._names = {}

    def ingest(self, data: NameData):
        # Prepare data for ingestion

        if not data.tags:
            # Assume full name
            data.add_tag('person')

        for subreading in data.subreadings:
            # Copy over the lifetime / source to the real actor
            if data.name_type == yomikun.models.NameType.PSEUDO \
                    and subreading.name_type == yomikun.models.NameType.REAL:
                if data.lifetime and not subreading.lifetime:
                    subreading.lifetime = copy.copy(data.lifetime)
                if data.source and not subreading.source:
                    subreading.source = data.source

        if 'person' in data.tags:
            self.add_person(data)

        for part, gender in self.extract_name_parts(data):
            if part not in self._names:
                self._names[part] = Name(
                    kaki=part.kaki,
                    yomi=part.yomi,
                    name_type=part.name_type,
                    earliest_year=data.lifetime.birth_year,
                    latest_year=data.lifetime.death_year,
                )
            else:
                self._names[part].record_year(data.lifetime.birth_year)
                self._names[part].record_year(data.lifetime.death_year)

            # Don't record non-person jmnedict entries as they are inaccurate.
            if data.source != 'jmnedict' or 'person' in data.tags:
                self._names[part].record_sighting(data.name_type)

            # NOTE: if we see >0 sightings of both gender we mark the
            # name as 'neutral' which may not be accurate in all cases.
            if gender:
                self._names[part].record_gender(gender)

            if data.source == 'myoji-yurai-5000' and part.name_type == NameType.sei:
                self._names[part].set_top5000()

            for subreading in data.subreadings:
                self.ingest(subreading)

    def people(self):
        return self._people

    def names(self):
        return self._names.values()

    def add_person(self, data: NameData):
        person = Person(kaki=data.kaki, yomi=data.yomi,
                        birth_year=data.lifetime.birth_year,
                        death_year=data.lifetime.death_year
                        )
        self._people.append(person)

    def extract_name_parts(self, data: NameData) -> list[tuple[NamePart, Gender | None]]:
        parts = []
        if 'person' in data.tags:
            # Rarely, is tagged [person, fem] to indicate the person's gender.
            gender = self.gender_from_tags(data.tags)
            kakis = data.kaki.split()
            yomis = data.yomi.split()
            if len(kakis) == 2 and len(yomis) == 2:
                sei = NamePart(kaki=kakis[0], yomi=yomis[0],
                               name_type=NameType.sei)
                mei = NamePart(kaki=kakis[1], yomi=yomis[1],
                               name_type=NameType.mei)
                parts += [(sei, gender), (mei, gender)]
            else:
                # Can't reliably assign name_types to names
                pass
        elif 'unclass' in data.tags:
            assert len(data.tags) == 1  # no other tags
            part = NamePart(kaki=data.kaki, yomi=data.yomi,
                            name_type=NameType.unknown)
            parts.append((part, None))
        else:
            # Names may be a combination of masc,fem,given,surname
            if 'surname' in data.tags:
                sei = NamePart(kaki=data.kaki, yomi=data.yomi,
                               name_type=NameType.sei)
                parts.append((sei, None))

            if set(data.tags).intersection({'masc', 'fem', 'given'}):
                gender = self.gender_from_tags(data.tags)
                mei = NamePart(kaki=data.kaki, yomi=data.yomi,
                               name_type=NameType.mei)
                parts.append((mei, gender))

        return parts

    @staticmethod
    def gender_from_tags(tags) -> Gender:
        if 'masc' in tags and 'fem' in tags:
            return Gender.neutral
        elif 'masc' in tags:
            return Gender.male
        elif 'fem' in tags:
            return Gender.female
        else:
            return Gender.unknown
