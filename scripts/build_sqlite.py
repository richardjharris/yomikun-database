"""
Loads final database (db/final.py=stdin) into an sqlite file (first argument)
"""

from __future__ import annotations
from itertools import zip_longest
import logging
import argparse
import sys
import os

import sqlite3
import json
import romkan

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

parser = argparse.ArgumentParser(
    description='Loads final database JSONL into an sqlite database',
    allow_abbrev=False,
)
parser.add_argument('dbfile', help='SQLite database filename')
args = parser.parse_args()

con = sqlite3.connect(args.dbfile)
cur = con.cursor()

cur.executescript("""
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
""")

PART_ID = {
    'unknown': 0,
    'sei': 1,
    'mei': 2,
}

def queries():
    for line in sys.stdin:
        row = json.loads(line)

        values = (
            row['kaki'],
            romkan.to_roma(row['yomi']),
            PART_ID[row['part']],
            row['hits_total'],
            row['hits_male'],
            row['hits_female'],
            row['hits_pseudo'],
            row.get('ml_score', 0),
        );

        yield [f"""
            INSERT INTO names(kaki,yomi,part,hits_total,hits_male,hits_female,hits_pseudo,ml_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, values]


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


for chunk in grouper(queries(), 10000):
    cur.execute('BEGIN TRANSACTION')
    for query in chunk:
        if query:
            cur.execute(*query)
    cur.execute('COMMIT')

cur.execute('VACUUM')
