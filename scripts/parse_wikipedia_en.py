#!/usr/bin/env python3

# Parses en.wikipedia.org dump and extracts Japanese names, dates of birth and gender.

from __future__ import annotations
import logging
import argparse
import sys
import json

import mwclient
from mediawiki_dump.dumps import MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from yomikun.wikipedia_en.parser import parse_wikipedia_article

parser = argparse.ArgumentParser(
    description="Parses en.wikipedia.org articles for name information.\n\n" +
    "Either pass articles via STDIN or provide an article name.",
    allow_abbrev=False,
)
parser.add_argument('article', nargs='*', help='Article title to parse')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Show important log messages (pass twice for more messages)')
args = parser.parse_args()

if args.verbose >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose >= 1:
    logging.basicConfig(level=logging.INFO)

if args.article:
    # Fetch article directly (uses local file cache)
    site = mwclient.Site('en.wikipedia.org')
    dump = MediaWikiClientDump(site, args.article)
    pages = DumpReaderArticles().read(dump)
    for page in pages:
        logging.debug(f'Page: {page.title}')
        result = parse_wikipedia_article(page.title, page.content)
        if result.has_name():
            print(result.to_jsonl())
else:
    for line in sys.stdin:
        data = json.loads(line)
        result = parse_wikipedia_article(data['title'], data['text'])
        if result.has_name():
            print(result.to_jsonl())
