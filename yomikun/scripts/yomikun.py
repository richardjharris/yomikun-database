"""
Entry point for all yomikun CLI commands. Handles common options.
"""
import click
import logging
from yomikun.commands import add_yomikun_commands


@click.group()
@click.option(
    '--loglevel',
    type=click.Choice(
        ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], case_sensitive=False
    ),
    default='WARNING',
    envvar='LOGLEVEL',
)
def cli(loglevel):
    logging.basicConfig(level=loglevel)


add_yomikun_commands(cli)


def main():
    cli(auto_envvar_prefix='YOMIKUN')
