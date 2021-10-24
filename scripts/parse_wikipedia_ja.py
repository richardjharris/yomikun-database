#!/usr/bin/env python3

# Parses ja.wikipedia.org dump and extracts names and dates of birth.

from __future__ import annotations
import logging
import argparse
import sys
import json
import os

import mwclient
from mediawiki_dump.dumps import MediaWikiClientDump
from mediawiki_dump.reader import DumpReaderArticles

from yomikun.wikipedia_ja.parser import parse_wikipedia_article

import traceback
import warnings
import sys

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

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
