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
    yomi TEXT,
    part TEXT,
    hits_total INT,
    hits_male INT,
    hits_female INT,
    hits_unknown INT,
    hits_pseudo INT,
    ml_score INT,
    PRIMARY KEY (kaki, yomi, part)
    );
    CREATE INDEX names_yomi ON names (yomi);
""")


def queries():
    for line in sys.stdin:
        row = json.loads(line)
        yield [f"""
            INSERT INTO names(kaki,yomi,part,hits_total,hits_male,hits_female,hits_unknown,hits_pseudo,ml_score)
            VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
        """, (row['kaki'], row['yomi'], row['part'], row['hits_total'], row['hits_male'], row['hits_female'], row['hits_unknown'],
              row['hits_pseudo'], row.get('ml_score', 0))]


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
