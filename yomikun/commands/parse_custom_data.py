import click
import sys
import logging
from glob import glob

from yomikun.custom_data.csv import parse_file

@click.command()
def parse_custom_data():
    """
    Parse custom.csv/custom.d name data

    Parse custom name data in data/custom.csv and data/custom.d/* and
    generate JSONL output.

    Custom name data uses a compact CSV format. Comments and extra
    whitespace are ignored.
    """
    for filename in ['data/custom.csv'] + glob('data/custom.d/*'):
        logging.info(f"Parsing {filename}")
        with open(filename) as input_file:
            parse_file(input_file, sys.stdout, input_filename=filename)
