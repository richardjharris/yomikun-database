#!/usr/bin/env python

# Entry point for all yomikun commands. Handles common options.
import click
import logging
from yomikun.commands import *

@click.group()
@click.option('--loglevel', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], case_sensitive=False), default='WARNING', envvar='LOGLEVEL')
def cli(loglevel):
    logging.basicConfig(level=loglevel)

cli.add_command(build_sqlite)

if __name__ == '__main__':
    cli(auto_envvar_prefix='YK')