import sqlite3
import sys
import click
import yomikun.sqlite.builder as builder

@click.command()
@click.argument('dbfile')
@click.option('--trace/--no-trace', help='Print all SQL statements to stderr')
def build_sqlite(dbfile, trace):
    """
    Build the final SQLite database as a new file DBFILE, using final.json
    output from STDIN.
    """
    connection = sqlite3.connect(dbfile)
    if trace:
        connection.set_trace_callback(lambda s: click.echo(s, err=True))
    builder.build_sqlite(connection)