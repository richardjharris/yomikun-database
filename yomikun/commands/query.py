import sqlite3
import sys

import click
import prettytable
import romkan

import yomikun.sqlite.query
from yomikun.sqlite.models import NamePart

# Mapping of sqlite column to header, in order
COLUMN_MAP = {
    'kaki': 'kaki',
    'yomi': 'yomi',
    'part': 'part',
    'hits': 'hits_total',
    'female': 'hits_female',
    'male': 'hits_male',
    'fict': 'hits_pseudo',
}


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

    cur = yomikun.sqlite.query.get_data(conn, search_term, part.lower(), limit)
    for row in cur.fetchall():
        row = dict(row)
        row['yomi'] = romkan.to_hiragana(row['yomi'])
        row['part'] = NamePart(row['part']).kanji

        printer.add_row(row)

    print(printer)


class PrettyPrinter:
    _table: prettytable.PrettyTable

    def __init__(self):
        table = prettytable.PrettyTable(COLUMN_MAP.keys())
        table.align = "r"
        table.align['yomi'] = 'l'  # type: ignore
        table.align['kaki'] = 'l'  # type: ignore
        table.align['part'] = 'l'  # type: ignore
        self._table = table

    def add_row(self, row: dict):
        self._table.add_row([row[v] for v in COLUMN_MAP.values()])

    def __str__(self):
        return str(self._table)


class TsvPrinter:
    _lines = []

    def __init__(self):
        self._lines.append('\t'.join(COLUMN_MAP.keys()))

    def add_row(self, row: dict):
        self._lines.append('\t'.join(str(row[v]) for v in COLUMN_MAP.values()))

    def __str__(self):
        return '\n'.join(self._lines)
