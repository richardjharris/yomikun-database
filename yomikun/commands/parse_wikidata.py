import click

import yomikun.wikidata.parse_wikidata as parser


@click.command()
@click.argument('input', type=click.File('r'), default='-')
@click.option(
    '--birth-name-file',
    type=click.File('r'),
    default='data/birth-names.jsonl',
    help='Path to birth name data file',
)
def parse_wikidata(input, birth_name_file):
    """
    Generate NameData from WikiData EN

    Convert queried wikidata results (from `yomikun fetch-wikidata`) from
    INPUT file (defaults to stdin) into JSONL format for dictionary loading.
    """
    parser.parse_wikidata(input, birth_name_file)
