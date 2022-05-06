import click

import yomikun.parsers.wikidata.parse_wikidata_nokana as parser


@click.command()
@click.argument('input', type=click.File('r'), default='-')
def parse_wikidata_nokana(input):
    """
    Generate NameData from WikiData JA

    Accepts wikidata on INPUT (default stdin) and outputs NameData JSONL to
    stdout.

    """
    parser.parse_wikidata_nokana(input)
