import sqlite3

import romkan

from yomikun.sqlite.models import NamePart
from yomikun.sqlite.table_builders.base import TableBuilderBase


class NamesTable(TableBuilderBase):
    """
    Class for generating the `names` table, which is the main table
    for all name reading and hit count data.
    """

    name = 'names'

    test_queries = [
        "SELECT COUNT(*) FROM names",
        "SELECT part, COUNT(*) FROM names GROUP BY part",
        "SELECT part, SUM(hits_total), SUM(hits_male), SUM(hits_female), SUM(hits_pseudo) FROM names GROUP BY part",  # noqa
        "SELECT * FROM names ORDER BY hits_total DESC LIMIT 20",
        "SELECT * FROM names WHERE yomi = 'shijou' ORDER BY hits_total DESC",
        "SELECT * FROM names WHERE kaki = '吉原' ORDER BY hits_total DESC",
        "SELECT * FROM names WHERE yomi = 'oono' ORDER BY hits_total DESC LIMIT 10",
        "SELECT * FROM names WHERE kaki = '大野' ORDER BY hits_total DESC LIMIT 10",
    ]

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

        # Convert part to part ID
        part_id = NamePart[row["part"]].value

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
