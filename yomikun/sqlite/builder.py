import json
import logging
import sqlite3
import sys
from datetime import datetime
from typing import IO

from yomikun.sqlite.tables.kanji_stats_table import KanjiStatsTable
from yomikun.sqlite.tables.names_table import NamesTable
from yomikun.sqlite.tables.quiz_table import QuizTable


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

    # The order of tables is important: quiz depends on names.
    tables = [NamesTable(), KanjiStatsTable(), QuizTable()]

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
