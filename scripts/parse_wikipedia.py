#!/usr/bin/env python3

# Parses incoming ja.wikipedia.org dump and extracts names and dates of birth.

from __future__ import annotations
import logging
import argparse

import mwclient
from mediawiki_dump.dumps import WikipediaDump, MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from wikipedia.parser import parse_wikipedia_article

parser = argparse.ArgumentParser(
    description='Parses ja.wikipedia.org articles for name information',
    allow_abbrev=False,
)
parser.add_argument('article', nargs='*', help='Article title(s) to parse')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Show important log messages (pass twice for more messages)')
args = parser.parse_args()

if args.verbose >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose >= 1:
    logging.basicConfig(level=logging.INFO)

if args.article:
    # Fetch article directly (uses local file cache)
    site = mwclient.Site('ja.wikipedia.org')
    dump = MediaWikiClientDump(site, args.article)
else:
    # Read dump file
    dump = WikipediaDump('ja')

pages = DumpReaderArticles().read(dump)
for page in pages:
    title = page.title
    content = page.content

    # TODO no way to distinguish "no name here" from "there's a name here,
    # but we failed to parse it"
    result = parse_wikipedia_article(title, content)
    if result.has_name():
        print(result.to_jsonl())
