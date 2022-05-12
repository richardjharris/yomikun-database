import sqlite3
from collections import defaultdict
from dataclasses import dataclass

import regex

from yomikun.sqlite.constants import PART_ID
from yomikun.sqlite.table_builders.base import TableBuilderBase


@dataclass(unsafe_hash=True)
class NameAndPart:
    kanji: str
    part: str  # as string


@dataclass
class GenderCounts:
    male: int = 0
    female: int = 0

    def add(self, new_male: int, new_female: int):
        self.male += new_male
        self.female += new_female

    @property
    def total(self):
        return self.male + self.female

    @property
    def female_ratio(self) -> int:
        if self.total == 0:
            return 127
        else:
            return int(self.female / self.total * 255)


class KanjiStatsTable(TableBuilderBase):
    """
    Class for generating the `kanji_stats` table, which holds per-kanji
    statistics.
    """

    name = 'kanji_stats'

    counts: defaultdict[NameAndPart, GenderCounts]

    is_han = regex.compile(r"\p{Han}")

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

        for ji in self.is_han.findall(row["kaki"]):
            key = NameAndPart(ji, part)
            self.counts[key].add(
                new_male=int(row["hits_male"]),
                new_female=int(row["hits_female"]),
            )

    def finish(self, cur: sqlite3.Cursor):
        for name_and_part, counts in self.counts.items():
            kanji = name_and_part.kanji
            part_id = PART_ID[name_and_part.part]

            # Insert stats for all genders combined
            cur.execute(
                "INSERT INTO kanji_stats VALUES(?, ?, 'A', ?, ?)",
                (kanji, part_id, counts.total, counts.female_ratio),
            )
            if name_and_part.part == 'mei':
                # Insert stats for male and female only
                cur.execute(
                    "INSERT INTO kanji_stats VALUES(?, ?, 'M', ?, 0)",
                    (kanji, part_id, counts.male),
                )
                cur.execute(
                    "INSERT INTO kanji_stats VALUES(?, ?, 'F', ?, 0)",
                    (kanji, part_id, counts.female),
                )
