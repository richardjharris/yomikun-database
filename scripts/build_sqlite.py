"""
Loads final database (db/final.py=stdin) into an sqlite file (first argument)
"""

from __future__ import annotations
from collections import defaultdict
from itertools import zip_longest
import logging
import argparse
import sys
import os

import sqlite3
import json
from xml.etree.ElementInclude import default_loader
import regex
import romkan


class KanjiCounts:
    counts: defaultdict[str, tuple[int, int]]

    is_han = regex.compile(r"\p{Han}")

    def __init__(self):
        self.counts = defaultdict(lambda: (0, 0))

    def handle(self, row):
        if row["part"] != "mei":
            return
        for ji in self.is_han.findall(row["kaki"]):
            m, f = self.counts[ji]
            self.counts[ji] = m + int(row["hits_male"]), f + int(row["hits_female"])

    def create_statement(self):
        return """
            CREATE TABLE kanji_stats(
                kanji TEXT,
                hits_total INT,
                female_ratio INT
            );
        """

    def score(self, mf: tuple[int, int]) -> int:
        m, f = mf
        if m + f == 0:
            return 127
        else:
            return int(m / (m + f) * 255)

    def insert_statements(self):
        sorted_entries = sorted(
            self.counts.items(), key=lambda x: self.score(x[1]), reverse=True
        )
        for entry in sorted_entries:
            ji, mf = entry
            m, f = mf
            yield [
                f"INSERT INTO kanji_stats VALUES(?, ?, ?)",
                (ji, m + f, self.score(mf)),
            ]


LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=LOGLEVEL)

parser = argparse.ArgumentParser(
    description="Loads final database JSONL into an sqlite database",
    allow_abbrev=False,
)
parser.add_argument("dbfile", help="SQLite database filename")
args = parser.parse_args()

kanji_counts = KanjiCounts()

con = sqlite3.connect(args.dbfile)
cur = con.cursor()

cur.executescript(
    """
    CREATE TABLE names(
        kaki TEXT,
        yomi TEXT, -- in romaji (saves 15% db size over kana)
        part INT,  -- 0=unknown 1=sei 2=mei (saves 15% over string)
        hits_total INT,
        hits_male INT,
        hits_female INT,
        hits_pseudo INT,
        ml_score INT,
        PRIMARY KEY (kaki, yomi, part, hits_total DESC)
    );
    CREATE INDEX names_yomi ON names (yomi, part, hits_total DESC);
"""
)
cur.executescript(kanji_counts.create_statement())

PART_ID = {
    "unknown": 0,
    "sei": 1,
    "mei": 2,
}


def queries(kanji_counts: KanjiCounts):
    for line in sys.stdin:
        row = json.loads(line)

        kanji_counts.handle(row)

        values = (
            row["kaki"],
            romkan.to_roma(row["yomi"]),
            PART_ID[row["part"]],
            row["hits_total"],
            row["hits_male"],
            row["hits_female"],
            row["hits_pseudo"],
            row.get("ml_score", 0),
        )

        yield [
            f"""
            INSERT INTO names(kaki,yomi,part,hits_total,hits_male,hits_female,hits_pseudo,ml_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            values,
        ]


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


kanji_counts = KanjiCounts()
for chunk in grouper(queries(kanji_counts), 10000):
    cur.execute("BEGIN TRANSACTION")
    for query in chunk:
        if query:
            cur.execute(*query)
    cur.execute("COMMIT")

for chunk in grouper(kanji_counts.insert_statements(), 10000):
    cur.execute("BEGIN TRANSACTION")
    for query in chunk:
        if query:
            cur.execute(*query)
    cur.execute("COMMIT")

cur.execute("VACUUM")
