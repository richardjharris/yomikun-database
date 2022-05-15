import sqlite3
from collections import defaultdict
from dataclasses import dataclass

import regex

from yomikun.sqlite.models import NamePart
from yomikun.sqlite.table_builders.base import TableBuilderBase


@dataclass(frozen=True)
class NameAndPart:
    kanji: str
    part: NamePart


@dataclass
class GenderCounts:
    male: int = 0
    female: int = 0
    unknown: int = 0

    def add(self, new_male: int, new_female: int, new_unknown: int):
        self.male += new_male
        self.female += new_female
        self.unknown += new_unknown

    @property
    def total(self):
        return self.male + self.female + self.unknown

    @property
    def female_ratio(self) -> int:
        male_and_female = self.male + self.female
        if male_and_female == 0:
            return 127
        else:
            return int(self.female / male_and_female * 255)


class KanjiStatsTable(TableBuilderBase):
    """
    Class for generating the `kanji_stats` table, which holds per-kanji
    statistics.
    """

    name = 'kanji_stats'

    counts: defaultdict[NameAndPart, GenderCounts]

    IS_HAN = regex.compile(r"\p{Han}")

    _create_statement = """
        CREATE TABLE kanji_stats(
            kanji TEXT,
            part INT,
            gender TEXT,
            hits_total INT,
            female_ratio INT -- from 0=all male to 255=all female; 127=neutral
        );
    """

    def create(self, cur: sqlite3.Cursor) -> None:
        cur.executescript(self._create_statement)

    def __init__(self):
        self.counts = defaultdict(GenderCounts)

    def handle_row(self, _cur, row: dict) -> None:
        part = row["part"]
        if part == "person":
            # already covered by mei/sei
            return

        for ji in self.IS_HAN.findall(row["kaki"]):
            key = NameAndPart(ji, NamePart[part.lower()])
            self.counts[key].add(
                new_male=int(row["hits_male"]),
                new_female=int(row["hits_female"]),
                new_unknown=int(row["hits_unknown"]),
            )

    def finish(self, cur: sqlite3.Cursor):
        for name_and_part, counts in self.counts.items():
            kanji = name_and_part.kanji
            part_id = name_and_part.part.value

            # Insert stats for all genders combined
            cur.execute(
                "INSERT INTO kanji_stats VALUES(?, ?, 'A', ?, ?)",
                (kanji, part_id, counts.total, counts.female_ratio),
            )
            if name_and_part.part == NamePart.mei:
                # Insert stats for male and female only
                cur.execute(
                    "INSERT INTO kanji_stats VALUES(?, ?, 'M', ?, 0)",
                    (kanji, part_id, counts.male),
                )
                cur.execute(
                    "INSERT INTO kanji_stats VALUES(?, ?, 'F', ?, 0)",
                    (kanji, part_id, counts.female),
                )
