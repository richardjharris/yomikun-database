import json
import logging
import sqlite3
import sys
from datetime import datetime
from typing import IO

from yomikun.sqlite.table_builders.kanji_stats_table import KanjiStatsTable
from yomikun.sqlite.table_builders.names_table import NamesTable
from yomikun.sqlite.table_builders.quiz_table import QuizTable

# The order of tables is important: quiz depends on names.
TABLES = [NamesTable, KanjiStatsTable, QuizTable]


def build_sqlite(connection: sqlite3.Connection, data_input: IO = sys.stdin) -> None:
    """
    Builds the Yomikun database using the supplied `connection`.

    Reads JSON namedata records from the handle `data_input`, defaulting to
    standard input.
    """
    cur = connection.cursor()

    # Autogenerate DB revision based on current time
    version = int(datetime.now().timestamp())
    cur.execute("PRAGMA user_version = " + str(version))
    logging.info("DB revision: %d", version)

    tables = [table() for table in TABLES]

    for table in tables:
        table.create(cur)

    for index, line in enumerate(data_input):
        row = json.loads(line)
        for table in tables:
            table.handle_row(cur, row)

        if index % 10000 == 0:
            connection.commit()

    for table in tables:
        table.finish(cur)

    connection.commit()

    logging.info("Vacuuming database...")
    cur.execute("VACUUM")
    logging.info("Done.")


def compare_databases(old: sqlite3.Connection, new: sqlite3.Connection):
    old_cur = old.cursor()
    new_cur = new.cursor()
    for table in TABLES:
        print(table.compare(old_cur, new_cur))


def get_test_queries():
    for table in TABLES:
        yield from table.test_queries
