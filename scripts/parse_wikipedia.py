#!/usr/bin/env python3

# Parses incoming ja.wikipedia.org dump and extracts names and dates of birth.

from __future__ import annotations
import logging

from mediawiki_dump.dumps import WikipediaDump
from mediawiki_dump.reader import DumpReaderArticles

from wikipedia.parser import parse_wikipedia_article

logging.basicConfig(level=logging.INFO)

dump = WikipediaDump('ja')
pages = DumpReaderArticles().read(dump)

for page in pages:
    title = page.title
    content = page.content

    result = parse_wikipedia_article(content)
    if result:
        print(result.to_jsonl())
