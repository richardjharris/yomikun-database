from collections import defaultdict
from typing import Any, Generator, Iterable

import regex

from yomikun.sqlite.constants import PART_ID, SqliteQuery


class KanjiStatsTable:
    """
    Class for generating the `kanji_stats` table, which holds per-kanji
    statistics.
    """

    # map (kanji. part_as_string) -> (male, female)
    counts: defaultdict[tuple[str, str], tuple[int, int]]

    is_han = regex.compile(r"\p{Han}")

    def __init__(self):
        self.counts = defaultdict(lambda: (0, 0))

    def handle(self, row: dict) -> None:
        part = row['part']
        if part == 'person':
            # already covered by mei/sei
            return

        for ji in self.is_han.findall(row["kaki"]):
            m, f = self.counts[(ji, part)]
            self.counts[(ji, part)] = m + int(row["hits_male"]), f + int(row["hits_female"])

    @staticmethod
    def create_statement() -> str:
        """
        Returns the SQL create statement(s) for this table.
        """
        return """
            CREATE TABLE kanji_stats(
                kanji TEXT,
                part INT,
                gender TEXT,
                hits_total INT,
                female_ratio INT -- from 0=all male to 255=all female; 127=neutral
            );
        """

    def insert_statements(self) -> Generator[SqliteQuery, None, None]:
        """
        Returns a generator yielding the SQL insert statements for this table.
        """
        sorted_entries = sorted(
            self.counts.items(), key=lambda x: self._female_ratio(x[1]), reverse=True
        )
        for entry in sorted_entries:
            key, mf = entry
            ji, part = key
            m, f = mf
            # All genders combined
            yield (
                f"INSERT INTO kanji_stats VALUES(?, ?, 'A', ?, ?)",
                (ji, PART_ID[part], m + f, self._female_ratio(mf)),
            )
            if part == 'mei':
                # Add male and female-only counts
                yield (
                    f"INSERT INTO kanji_stats VALUES(?, ?, 'M', ?, 0)",
                    (ji, PART_ID[part], m),
                )
                yield (
                    f"INSERT INTO kanji_stats VALUES(?, ?, 'F', ?, 0)",
                    (ji, PART_ID[part], f),
                )

    def _female_ratio(self, mf: tuple[int, int]) -> int:
        m, f = mf
        if m + f == 0:
            return 127
        else:
            return int(f / (m + f) * 255)