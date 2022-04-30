from __future__ import annotations
import logging
import sys
import json
import click

import mwclient
from mediawiki_dump.dumps import MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from yomikun.wikipedia_en.parser import parse_wikipedia_article

@click.command()
@click.argument('article', nargs=-1)
@click.option('-v', '--verbose', count=True, help='Show important log messages (pass twice for more)')
def parse_wikipedia_en(verbose, articles):
    """
    Parse en.wikipedia.org dump

    Parses ARTICLE(s), if provided, otherwise expects JSONL-converted article data on stdin.
    
    Extracts names (including aliases), date of birth/death, gender, description.

    Wikipedia romaji names have a somewhat inconsistent format. To handle ambiguous
    cases, RomajiDB is used, otherwise we fall back to assuming an 'o' is a short vowel
    and a 'ō' is a long vowel.
    """
    # Does not filter out 'User' pages as they contain good quality names - in some cases
    # the only source for a particular name.
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose >= 1:
        logging.basicConfig(level=logging.INFO)

    if articles:
        # Fetch article directly (uses local file cache)
        site = mwclient.Site('en.wikipedia.org')
        dump = MediaWikiClientDump(site, articles)
        pages = DumpReaderArticles().read(dump)
        for page in pages:
            logging.debug(f'Page: {page.title}')
            if result := parse_wikipedia_article(page.title, page.content):
                print(result.to_jsonl())
    else:
        for line in sys.stdin:
            data = json.loads(line)
            try:
                if result := parse_wikipedia_article(data['title'], data['text']):
                    print(result.to_jsonl())
            except ValueError as e:
                logging.error(f"Error processing article {data['title']}: {e}")
