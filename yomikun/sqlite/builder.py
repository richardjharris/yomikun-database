from datetime import datetime
from itertools import zip_longest
import json
import sqlite3
import sys
from typing import IO, Generator, Iterable
from yomikun.sqlite.constants import SqliteQuery

from yomikun.sqlite.kanji_stats_table import KanjiStatsTable
from yomikun.sqlite.names_table import NamesTable
from yomikun.sqlite.quiz_table import QuizTable


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
    print("Generated DB version {}".format(version), file=sys.stderr)

    names_table = NamesTable()
    cur.executescript(names_table.create_statement())

    kanji_stats_table = KanjiStatsTable()
    cur.executescript(kanji_stats_table.create_statement())

    def process_input() -> Generator[SqliteQuery, None, None]:
        # Process the input. Lazily generates a list of queries to execute for the
        # names table.
        for line in data_input:
            row = json.loads(line)
            kanji_stats_table.handle(row)

            yield names_table.make_query(row)

    def batch_execute(stream: Iterable[SqliteQuery], batch_size: int = 10000):
        for batch in _split_into_batches(stream, batch_size):
            for query in batch:
                if query:
                    cur.execute(*query)
            connection.commit()

    names_table_queries = process_input()
    batch_execute(names_table_queries)

    # Now all the rows have been processed, we can generate queries for aggregate
    # data.
    batch_execute(kanji_stats_table.insert_statements())

    quiz_table = QuizTable()
    quiz_table.create(cur)

    connection.commit()

    cur.execute("VACUUM")


def _split_into_batches(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
