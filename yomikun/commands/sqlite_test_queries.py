import click

from yomikun.sqlite import builder


@click.command()
def sqlite_test_queries():
    """
    Outputs a list of test queries to run against the SQLite database.
    """
    for query in builder.get_test_queries():
        click.echo(query + ';\n')
