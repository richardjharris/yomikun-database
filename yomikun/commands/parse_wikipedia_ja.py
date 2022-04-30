from __future__ import annotations
import logging
import json
import sys
import click

import mwclient
from mediawiki_dump.dumps import MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from yomikun.wikipedia_ja.parser import parse_wikipedia_article


@click.command()
@click.argument('article', nargs=-1)
@click.option(
    '-v',
    '--verbose',
    count=True,
    help='Show important log messages (pass twice for more)',
)
def parse_wikipedia_ja(verbose, articles):
    """
    Parses ja.wikipedia.org dump

    Parses ARTICLE(s), if provided, otherwise expects JSONL-converted article data on stdin.

    Extracts names (including aliases), date of birth/death, gender, description.
    """
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose >= 1:
        logging.basicConfig(level=logging.INFO)

    if articles:
        # Fetch article directly (uses local file cache)
        site = mwclient.Site('ja.wikipedia.org')
        dump = MediaWikiClientDump(site, articles)
        pages = DumpReaderArticles().read(dump)
        for page in pages:
            # TODO no way to distinguish "no name here" from "there's a name here,
            # but we failed to parse it"
            if result := parse_wikipedia_article(page.title, page.content):
                print(result.to_jsonl())
    else:
        for line in sys.stdin:
            data = json.loads(line)
            if result := parse_wikipedia_article(data['title'], data['text']):
                print(result.to_jsonl())
