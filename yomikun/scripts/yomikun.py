"""
Entry point for all yomikun CLI commands. Handles common options.
"""
import logging
import click
from yomikun.commands import add_yomikun_commands


@click.group()
@click.option(
    '--loglevel',
    type=click.Choice(
        ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NONE'], case_sensitive=False
    ),
    default='WARNING',
    envvar='LOGLEVEL',
)
@click.option(
    '-v',
    '--verbose',
    count=True,
    help='Show detailed log messages (pass twice for more)',
)
@click.version_option()
def cli(loglevel, verbose):
    if verbose > 0:
        if loglevel:
            raise Exception("cannot specify -v and --loglevel together")
        loglevel = 'DEBUG' if verbose >= 2 else 'INFO'

    if loglevel != 'NONE':
        logging.basicConfig(level=loglevel)


add_yomikun_commands(cli)


def main():
    cli(auto_envvar_prefix='YOMIKUN')
