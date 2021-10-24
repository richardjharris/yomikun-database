"""
Builds the final database.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
import dataclasses
import json
import logging
import sys
from typing import Iterable, TextIO, cast
from isc import keydict

import regex
import jcconv3
import romkan
from yomikun.gender.dict import GenderDict

from yomikun.loader.aggregator import Aggregator, NamePart
from yomikun.loader.models import Gender, NamePosition
from yomikun.models import NameData
from yomikun.models.lifetime import Lifetime
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.utils.romaji.helpers import romaji_key


@dataclass
class AggregatedData():
    hits_male: int = 0
    hits_female: int = 0
    hits_unknown: int = 0
    years_seen: Lifetime = field(default_factory=Lifetime)
    hits_xx_romaji: int = 0
    hits_pseudo: int = 0
    is_top5k: bool = False
    population: int = 0

    def hits_total(self):
        return self.hits_male + self.hits_female + self.hits_unknown

    def record_hit(self, part: NamePart, gender: Gender, name: NameData):
        if name.has_tag('dict'):
            # Does not count as a hit
            return

        print(part, gender, name)

        self._record_gender_hit(gender)
        self.years_seen.expand(name.lifetime)
        # TODO this should only apply to the particular part
        if name.has_tag('xx-romaji'):
            self.hits_xx_romaji += 1
        if name.authenticity != NameAuthenticity.REAL:
            self.hits_pseudo += 1

    def _record_gender_hit(self, gender: Gender):
        if gender == Gender.male:
            self.hits_male += 1
        elif gender == Gender.female:
            self.hits_female += 1
        elif gender == Gender.unknown:
            self.hits_unknown += 1
        else:
            raise Exception(f'Unknown Gender value: {gender}')

    def to_dict(self):
        row = dataclasses.asdict(self)
        row['hits_total'] = self.hits_total()
        if not self.is_top5k:
            del row['is_top5k']
            del row['population']
        return row

    def mark_top5k(self, population: int):
        self.is_top5k = True
        self.population = population


def make_final_db(names: Iterable[NameData], db_out: TextIO):
    genderdb = GenderDict()

    DictKey = tuple[str, str, NamePosition]
    aggregated_data: dict[DictKey,
                          AggregatedData] = defaultdict(AggregatedData)

    for name in names:
        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            kana = part.yomi

            # Some jmnedict results currently contain katakana
            kana = cast(str, jcconv3.kata2hira(kana))

            kaki = part.kaki
            pos = part.position
            gender = gender or Gender.unknown

            key = (kaki, kana, pos)

            aggregated_data[key].record_hit(part, gender, name)

            if name.has_tag('top5k'):
                population = 0
                if m := regex.match(r'^population:(\d+)$', name.notes):
                    population = int(m[1])

                aggregated_data[key].mark_top5k(population)

    # Output aggregated data
    for key, aggregated in aggregated_data.items():
        kaki, kana, pos = key

        row = aggregated.to_dict()
        row['kaki'] = kaki
        row['yomi'] = kana
        row['pos'] = pos.name

        if info := genderdb.lookup(kaki, kana):
            row.update(info.to_dict())

        print(json.dumps(row, ensure_ascii=False))
