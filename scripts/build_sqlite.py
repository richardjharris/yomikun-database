"""
Loads final database (db/final.py=stdin) into an sqlite file (first argument)
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from itertools import zip_longest
import logging
import argparse
import sys
import os

import sqlite3
from yomikun.sqlite.builder import build_sqlite

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=LOGLEVEL)

parser = argparse.ArgumentParser(
    description="Loads final database JSONL into an sqlite database",
    allow_abbrev=False,
)
parser.add_argument("dbfile", help="SQLite database filename")
parser.add_argument("--trace", action='store_true', help="Print all SQL statements to stderr")
args = parser.parse_args()

connection = sqlite3.connect(args.dbfile)
if args.trace:
    connection.set_trace_callback(lambda s: print(s, file=sys.stderr))

build_sqlite(connection)
