import sqlite3

import romkan

from yomikun.sqlite.constants import PART_ID
from yomikun.sqlite.table_builders.base import TableBuilderBase


class NamesTable(TableBuilderBase):
    """
    Class for generating the `names` table, which is the main table
    for all name reading and hit count data.
    """

    name = 'names'

    _create_statement = """
        CREATE TABLE names(
            kaki TEXT,
            yomi TEXT, -- in romaji (saves 15% db size over kana)
            part INT,  -- 0=unknown 1=sei 2=mei (saves 15% over string)
            hits_total INT,
            hits_male INT,
            hits_female INT,
            hits_pseudo INT,
            female_ratio INT, -- from 0=all male to 255=all female; 127=neutral
            PRIMARY KEY (kaki, yomi, part, hits_total DESC)
        );
        CREATE INDEX names_yomi ON names (yomi, part, hits_total DESC);
    """

    def create(self, cur: sqlite3.Cursor) -> None:
        cur.executescript(self._create_statement)

    def handle_row(self, cur: sqlite3.Cursor, row: dict):
        # Convert yomi to romaji so it takes up less space
        yomi = romkan.to_roma(row["yomi"])

        # romkan eagerly adds apostrophes in places where we don't really need them,
        # e.g. "anna" does not need to be "an'na".
        yomi = yomi.replace("n'n", "nn")

        # Convert part to part ID
        part_id = PART_ID[row["part"]]

        values = (
            row["kaki"],
            yomi,
            part_id,
            row["hits_total"],
            row["hits_male"],
            row["hits_female"],
            row["hits_pseudo"],
            row.get("ml_score", 0),
        )

        cur.execute(
            """
                INSERT INTO names(
                    kaki,yomi,part,hits_total,hits_male,hits_female,hits_pseudo,female_ratio
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
