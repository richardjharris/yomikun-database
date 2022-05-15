import sqlite3
import sys

import click
import prettytable
import regex
import romkan

from yomikun.sqlite.models import NamePart

HEADER_NAMES = ["kaki", "yomi", "part", "hits", "female", "male", "fict"]
SQL_COLUMN_NAMES = [
    "kaki",
    "yomi",
    "part",
    "hits_total",
    "hits_female",
    "hits_male",
    "hits_pseudo",
]


@click.command()
@click.argument('search_term')
@click.option(
    '--dbfile',
    type=str,
    help='Path to the Yomikun database file.',
    default='db/final.db',
)
@click.option(
    '--part',
    type=click.Choice(['all', 'sei', 'mei', 'unknown']),
    default='all',
    help='The type of the name to search for.',
)
@click.option('--trace/--no-trace', help='Print all SQL statements to stderr')
@click.option(
    '--limit',
    help='Maximum number of results to display. Use -1 for no limit.',
    type=int,
    default=10,
)
def query(search_term, dbfile, part, trace, limit):
    """
    Query the Yomikun database.
    """
    conn = sqlite3.connect(dbfile)
    if trace:
        conn.set_trace_callback(lambda s: click.echo(s, err=True))

    printer = PrettyPrinter() if sys.stdout.isatty() else TsvPrinter()

    cur = get_data(conn, search_term, part.lower(), limit)
    for row in cur.fetchall():
        row = dict(row)
        row['yomi'] = romkan.to_hiragana(row['yomi'])
        row['part'] = NamePart(row['part']).kanji

        printer.add_row(row)

    print(printer)


class PrettyPrinter:
    _table: prettytable.PrettyTable

    def __init__(self):
        table = prettytable.PrettyTable(HEADER_NAMES)
        table.align = "r"
        table.align['yomi'] = 'l'  # type: ignore
        table.align['kaki'] = 'l'  # type: ignore
        table.align['part'] = 'l'  # type: ignore
        self._table = table

    def add_row(self, row: dict):
        self._table.add_row(row.values())

    def __str__(self):
        return str(self._table)


class TsvPrinter:
    _lines = []

    def __init__(self):
        self._lines.append('\t'.join(HEADER_NAMES))

    def add_row(self, row: dict):
        self._lines.append('\t'.join(map(str, row.values())))

    def __str__(self):
        return '\n'.join(self._lines)


def get_data(
    conn: sqlite3.Connection, search_term: str, part: str, limit: int
) -> sqlite3.Cursor:
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row  # type: ignore

    is_kaki = regex.match(r'\p{Han}', search_term)
    if is_kaki:
        query_col = 'kaki'
    else:
        query_col = 'yomi'
        search_term = romkan.to_roma(search_term)

    if part == 'all':
        part_query = ""
    else:
        part_id = NamePart[part].value
        part_query = f"AND part = {int(part_id)}"

    limit_sql = '' if limit == -1 else f'LIMIT {int(limit)}'

    sql = f"""
        SELECT {', '.join(SQL_COLUMN_NAMES)} FROM names
        WHERE {query_col} = ? {part_query}
        ORDER BY part, hits_total DESC
        {limit_sql}
    """
    cur.execute(sql, (search_term))
    return cur
