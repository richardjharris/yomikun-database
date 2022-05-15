import logging
import sqlite3
from pathlib import Path

import click

from yomikun.sqlite import builder


@click.command()
@click.argument('dbfile', type=click.Path(dir_okay=False, path_type=Path))
@click.option('--trace/--no-trace', help='Print all SQL statements to stderr')
@click.option('--replace/--no-replace', help='Overwrite an existing database')
def build_sqlite(dbfile: Path, trace: bool, replace: bool):
    """
    Build final SQLite database

    Build the final SQLite database as a new file DBFILE, using aggregated.jsonl
    output from STDIN.
    """
    oldcopy = None

    if dbfile.exists():
        if replace:
            oldcopy = dbfile.with_suffix('.old')
            dbfile.rename(oldcopy)
            logging.warning('Old database copied to %s', oldcopy)
        else:
            raise click.ClickException(
                f'{dbfile} already exists, use --replace to overwrite'
            )

    connection = sqlite3.connect(dbfile)
    if trace:
        connection.set_trace_callback(lambda s: click.echo(s, err=True))
    builder.build_sqlite(connection)

    if oldcopy:
        old_connection = sqlite3.connect(oldcopy)
        builder.compare_databases(old_connection, connection)
