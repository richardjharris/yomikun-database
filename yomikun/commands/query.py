import click


@click.command()
@click.option(
    '--dbfile',
    type=str,
    help='Path to the Yomikun database file.',
    default='db/final.db',
)
def query(dbfile):
    """
    Query the Yomikun database.
    """
    click.echo(f'DB file = {dbfile}')
