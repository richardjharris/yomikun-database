import click
import prettytable
import regex
import romkan
import sqlite3
import sys

PARTS_IN_DATABASE_ORDER = ['unknown', 'sei', 'mei']


@click.command()
@click.argument('query')
@click.option(
    '--dbfile',
    type=str,
    help='Path to the Yomikun database file.',
    default='db/final.db',
)
@click.option(
    '--mode',
    type=click.Choice(['sei', 'mei', 'unknown']),
    required=True,
    default='sei',
)
@click.option('--trace/--no-trace', help='Print all SQL statements to stderr')
@click.option(
    '--limit',
    help='Maximum number of results to display. Use -1 for no limit.',
    type=int,
    default=10,
)
def query(query, dbfile, mode, trace, limit):
    """
    Query the Yomikun database.
    """
    conn = sqlite3.connect(dbfile)
    if trace:
        conn.set_trace_callback(lambda s: click.echo(s, err=True))
    cur = get_data(conn, query, mode, limit)
    if sys.stdout.isatty():
        print_pretty_table(cur)
    else:
        print_tsv(cur)


def print_pretty_table(cur: sqlite3.Cursor):
    table = prettytable.from_db_cursor(cur)
    table.align = 'r'
    table.align['yomi'] = 'l'  # type: ignore
    table.align['kaki'] = 'l'  # type: ignore
    print(table)


def print_tsv(cur: sqlite3.Cursor):
    print("kaki\tyomi\thits\tfemale\tmale\tpseudo")
    for row in cur.fetchall():
        print(
            "\t".join(
                [
                    row['kaki'],
                    romkan.to_hiragana(row['yomi']),
                    str(row['hits_total']),
                    str(row['hits_female']),
                    str(row['hits_male']),
                ]
            )
        )


def get_data(
    conn: sqlite3.Connection, query: str, mode: str, limit: int
) -> sqlite3.Cursor:
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row

    is_kaki = regex.match(r'\p{Han}', query)
    if is_kaki:
        query_col = 'kaki'
    else:
        query_col = 'yomi'
        query = romkan.to_roma(query)

    part_id = PARTS_IN_DATABASE_ORDER.index(mode)
    limit_sql = '' if limit == -1 else f'LIMIT {int(limit)}'

    sql = f"""
        SELECT * FROM names
        WHERE {query_col} = ? AND part = ?
        ORDER BY hits_total DESC
        {limit_sql}
    """
    cur.execute(sql, (query, part_id))
    return cur
