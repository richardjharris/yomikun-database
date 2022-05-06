from __future__ import annotations

import json
import logging
import sys

import click
import mwclient
from mediawiki_dump.dumps import MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from yomikun.parsers.wikipedia_en.parser import parse_wikipedia_article as parse_en
from yomikun.parsers.wikipedia_ja.parser import parse_wikipedia_article as parse_ja

PARSERS = {
    'en': parse_en,
    'ja': parse_ja,
}


@click.command()
@click.argument('articles', nargs=-1, metavar='ARTICLE')
@click.option(
    '--lang', help='Wikipedia language', type=click.Choice(['en', 'ja']), required=True
)
def parse_wikipedia(articles, lang):
    """
    Parse en/ja.wikipedia.org dump

    Parses ARTICLE(s), if provided, otherwise expects JSONL-converted article data on stdin.

    Extracts names (including aliases), date of birth/death, gender, description.
    """
    hostname = f'{lang}.wikipedia.org'
    parser = PARSERS[lang]

    # Does not filter out 'User' pages as they contain good quality names - in some cases
    # the only source for a particular name.
    if articles:
        # Fetch article directly (uses local file cache)
        site = mwclient.Site(hostname)
        dump = MediaWikiClientDump(site, articles)
        pages = DumpReaderArticles().read(dump)
        for page in pages:
            logging.debug(f'Page: {page.title}')
            if result := parser(page.title, page.content):
                print(result.to_jsonl())
    else:
        for line in sys.stdin:
            data = json.loads(line)
            try:
                if result := parser(data['title'], data['text']):
                    print(result.to_jsonl())
            except ValueError as e:
                logging.error(f"Error processing article {data['title']}: {e}")
