"""
Builds the final database.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
import logging
import sys
from typing import Iterable, TextIO, cast

import regex
import jcconv3
import romkan

from yomikun.loader.aggregator import Aggregator, NamePart
from yomikun.loader.models import Gender, NamePosition
from yomikun.models import NameData
from yomikun.models.lifetime import Lifetime
from yomikun.utils.romaji.helpers import romaji_key


@dataclass
class AggregatedData():
    hits_male: int = 0
    hits_female: int = 0
    hits_unknown: int = 0
    years_seen: Lifetime = field(default_factory=Lifetime)
    hits_xx_romaji: int = 0
    hits_pseudo: int = 0

    def hits_total(self):
        return self.hits_male + self.hits_female + self.hits_unknown

    def record_hit(self, part: NamePart, gender: Gender, name: NameData):
        if name.has_tag('dict'):
            # Does not count as a hit
            return

        self._record_gender_hit(gender)
        self.years_seen.expand(name.lifetime)
        # TODO this should only apply to the particular part
        if name.has_tag('xx-romaji'):
            self.hits_xx_romaji += 1
        if name.has_tag('pseudo') or name.has_tag('fictional'):
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
        row = dataclass.asdict(self)
        row['hits_total'] = self.hits_total()
        return row


def make_final_db(names: Iterable[NameData], db_out: TextIO):
    # Aggregate data
    DictKey = tuple[str, str, NamePosition]

    data: dict[DictKey, AggregatedData] = defaultdict(AggregatedData)
    for name in names:
        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            kana = part.yomi

            assert not regex.search(r'\p{Katakana}', kana)

            kaki = part.kaki
            pos = part.position

            data[(kaki, kana, pos)].record_hit(
                part, gender or Gender.unknown, name)

    # Output aggregated data
    for key, aggregated in data.items():
        kaki, kana, pos = key

        row = aggregated.to_dict()
        row['kaki'] = kaki
        row['yomi'] = kana
        row['pos'] = pos.name

    # TODO: gender ML stuff (gender dict / gender ML)
    # TODO: people (de-duped Person data)
    # TODO: top5k stuff
