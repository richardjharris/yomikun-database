import sqlite3

import regex

from yomikun.sqlite.tables.base import TableBase


class QuizTable(TableBase):
    _create_statement = """
        CREATE TABLE quiz AS
            WITH most_common AS (
                SELECT
                    kaki,
                    part,
                    SUM(hits_total) total
                FROM names
                GROUP BY kaki, part
                ORDER BY total DESC
            ),
            -- For top N kaki, get all readings and filter to those with >20% share.
            ungrouped AS (
                SELECT
                    names.kaki,
                    names.part,
                    yomi,
                    hits_total,
                    most_common.total,
                    hits_total*1.0/most_common.total pc
                FROM names
                JOIN most_common ON most_common.kaki = names.kaki
                    AND most_common.part = names.part
                WHERE pc > 0.2
                ORDER BY names.kaki, names.part
            )
            -- Group concat the readings so we return one row per kaki.
            -- Don't include very rare readings.
            SELECT
                kaki,
                part,
                GROUP_CONCAT(yomi) yomi,
                SUM(total) total
            FROM ungrouped
            GROUP BY kaki, part
            HAVING total >= 75
    """

    def finish(self, cur: sqlite3.Cursor):
        # Create table in finish() as we use the 'names' table to create it.
        cur.executescript(self._create_statement)

        # Remove hiragana-only kaki entries, as these won't pose any challenge.
        cur.execute("SELECT kaki FROM quiz")
        if cur.rowcount == 0:
            raise Exception("no data in 'quiz' table!")

        kaki_list = [row for row in cur if regex.search(r"^\p{Hiragana}+$", row[0])]
        cur.executemany("DELETE FROM quiz WHERE kaki = ?", kaki_list)
