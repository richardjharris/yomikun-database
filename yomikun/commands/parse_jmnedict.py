"""
JMnedict parser and NameData generator.

The JMnedict is extremely comprehensive, but this causes problems - it contains
extremely rare readings, made-up names, and the name type is often incorrect.
For example many names are marked up as both a given name and a surname despite this
being very rare in Japanese.

Our strategy here is to import all of it, then use Wikipedia and other data to
identify the readings that are actually seen in the real world. For this reason we
also import 'unclass'-type names that are not confirmed to be person names at all.
These would show up dead last in a dictionary lookup, but are good for completeness.
"""
import click

import yomikun.utils.jmnedict
from yomikun.parsers.jmnedict import parser


@click.command()
def parse_jmnedict():
    """
    Generate NameData from JMnedict

    Uses the JMnedict file that is installed as part of the Python `jamdict-data`
    package (no input required). Extracts full names and lifetimes, as well as
    individual surnames and given names. Output is in JSONL format.

    Gender information (masc/fem tag) is ignored as it is usually inaccurate.
    Also, entries are tagged 'dict' to indicate that they are not real world name
    sightings. Such entries do not count as a 'hit' in aggregated statistics.
    """
    for data in yomikun.utils.jmnedict.all_jmnedict_data():
        for name in parser.parse_jmnedict_entry(data):
            print(name.to_jsonl())
