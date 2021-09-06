#!/usr/bin/env python3

# Parses en.wikipedia.org dump and extracts Japanese names, dates of birth and gender.

from __future__ import annotations
import logging
import argparse

import mwclient
from mediawiki_dump.dumps import WikipediaDump, MediaWikiClientDump, LocalWikipediaDump
from mediawiki_dump.reader import DumpReaderArticles
import usb

from yomikun.wikipedia_en.parser import parse_wikipedia_article

parser = argparse.ArgumentParser(
    description='Parses en.wikipedia.org articles for name information',
    allow_abbrev=False,
)
parser.add_argument('article', nargs='*', help='Article title(s) to parse')
parser.add_argument('-d', '--dump', type=str, help='Load local dump file')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Show important log messages (pass twice for more messages)')
args = parser.parse_args()

if args.article and args.dump:
    parser.error('Cannot past --dump AND an article name')

if args.verbose >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose >= 1:
    logging.basicConfig(level=logging.INFO)

if args.article:
    # Fetch article directly (uses local file cache)
    site = mwclient.Site('en.wikipedia.org')
    dump = MediaWikiClientDump(site, args.article)
elif args.dump:
    logging.info(f'Using local dump file {args.dump}')
    dump = LocalWikipediaDump(args.dump)
else:
    # Read dump file
    logging.info('Reading wikipedia dump file')
    dump = WikipediaDump('en')

logging.info('Calling read(dump)')
pages = DumpReaderArticles().read(dump)
for page in pages:
    title = page.title
    content = page.content
    logging.debug(f'Page: {title}')

    if 'ihongo' not in content:
        continue

    result = parse_wikipedia_article(title, content)
    if result.has_name():
        print(result.to_jsonl())
