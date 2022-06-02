"""
Builds the final database.
"""


import dataclasses
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, TextIO

import jcconv3
import regex

from yomikun.gender.dict import GenderDict
from yomikun.models import Gender, Lifetime, NameAuthenticity, NameData, NameDataKey


@dataclass
class AggregatedData:
    """
    Aggregate data (number of people, male/female) for a given forename
    or surname.
    """

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

    def record_hit(self, gender: Gender, name: NameData):
        if name.is_dict:
            # Does not count as a hit
            return

        self._record_gender_hit(gender)
        self.years_seen.expand(name.lifetime)
        if 'xx-romaji' in name.tags:
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


def build_aggregated_data(
    names_in: Iterable[NameData], genderdb_file_in: str, db_out: TextIO
):
    """
    Given input name records (which can be people or individual name parts)
    aggregate the data and produce output in JSONL format suitable for
    importing into SQLite. This text is sent to [db_out].
    """
    aggregated_data: dict[NameDataKey, AggregatedData] = defaultdict(AggregatedData)

    for name in names_in:
        for part in name.extract_name_parts():
            kana = part.yomi

            # Some jmnedict results currently contain katakana
            # FIXME: kana is currently ignored
            kana = jcconv3.kata2hira(kana)

            aggregated_data[part.key()].record_hit(part.gender, name)

            if name.source == 'myoji-yurai-5000':
                population = 0
                if m := regex.search(r'^population:(\d+)$', name.notes):
                    population = int(m[1])

                aggregated_data[part.key()].mark_top5k(population)

    _output_aggregated_data(aggregated_data, genderdb_file_in, db_out)


def _output_aggregated_data(
    aggregated_data: dict[NameDataKey, AggregatedData],
    genderdb_file_in: str,
    db_out: TextIO,
):
    genderdb = GenderDict(genderdb_file_in)

    # Output aggregated data
    for name, aggregated in aggregated_data.items():
        row = aggregated.to_dict()
        row['kaki'] = name.kaki
        row['yomi'] = name.yomi
        row['part'] = name.position.name

        if info := genderdb.lookup(name.kaki, name.yomi):
            row.update(info.to_dict())
            # Convert ml_score to sqlite int 0-255
            row['ml_score'] = ml_score_float_to_int(row.get('ml_score', 0))

        print(json.dumps(row, ensure_ascii=False), file=db_out)


def ml_score_float_to_int(score: float) -> int:
    """
    Convert ml_score into an int between 0 and 255 so it occupies 1 byte
    instead of 8 (for a float)

    If |score| > 3 it is capped at 3.
    """
    if score == 0:
        return 128
    else:
        ml_sign = 1 if score > 0 else -1
        score = min(abs(score), 3)
        return int((ml_sign * (score / 3.0) * 127.5) + 127.5)


def test_ml_score_float_to_int():
    assert ml_score_float_to_int(3) == 255
    assert ml_score_float_to_int(4) == 255
    assert ml_score_float_to_int(1.5) == (127 + 255) / 2.0
    assert ml_score_float_to_int(0) == 128
    assert ml_score_float_to_int(-1.5) == 63
    assert ml_score_float_to_int(-3) == 0
    assert ml_score_float_to_int(-10) == 0
