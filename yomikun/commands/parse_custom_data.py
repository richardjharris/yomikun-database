import sys
import logging
import click


from yomikun.custom_data.csv import parse_file


@click.command()
@click.argument('input', type=click.File('r'), nargs=-1)
def parse_custom_data(input):
    """
    Parse custom.csv/custom.d name data

    Parse custom name data from the given file(s), and output
    NameData JSONL on stdout.

    Custom name data uses a compact CSV format. Comments and extra
    whitespace are ignored.
    """
    if not input:
        input = [sys.stdin]

    for file in input:
        logging.info(f"Parsing {file.name}")
        if not parse_file(file, sys.stdout, input_filename=file.name):
            sys.exit(1)
