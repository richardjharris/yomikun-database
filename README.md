### yomikun-database

![Unit test status](https://github.com/richardjharris/yomikun-database/actions/workflows/tests.yml/badge.svg?event=push)
![Test coverage status](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/richardjharris/yomikun-database/python-coverage-comment-action-badge.json)

Scripts and modules to generate the name database used by Yomikun.

This includes:

- parsing Wikipedia and other dictionary data
  - handling ambiguous romaji
- collecting gender information
  - uses a ML model to guess if no data exists
- generating lists such as top 1000 lists
- assembling the data into an SQLite file

## Prerequisites

Code: Python 3.10, the modules in `requirements.txt` (and `requirements-dev.txt`
for development). See the `prep*` makefile targets.

Makefile: a Linux-compatible environment with `moreutils` (`parallel` tool),
`pzcat` (to be added). For fast conversion of MediaWiki XML dumps to JSON,
Perl and the `MediaWiki::DumpFile::FastPages` module is used. If you don't
want to use Perl, you can do the conversion yourself quite easily.

At present I use several personal data sources to generate the name database,
so the makefile will not run as-is. To build a simple version, you can remove
any data sources that won't build, and provide `enwiki.xml.bz2` and `jawiki.xml.bz2`
from Mediawiki dumps.

## Directory structure

- data: raw data used by other scripts
- jsonl: prepared name data generated by scripts/data sources for assembly
  into the final database, in JSONL format
- db: final output files
- notes: todo, findings, other resources
- scripts: command line scripts
- tests: global unit tests (other tests are inside each .py file)
- tmp: tmp directory for makefile (sorts etc)
- yomikun: python code
 - commands - CLI subcommand logic
 - gender - name to gender guesser
 - jmnedict - related to JMnedict parsing
 - loader - assembles the final database
 - models - general-purpose classes used by everything (NameData is the most important)
 - parsers - parsing code
   - daijisen - Daijisen dictionary
   - wikidata - WikiData EN/JA
   - wikipedia_en - Wikipedia EN
   - wikipedia_ja - Wikipedia JA
   - koujien.py - Koujien dictionary
   - pdd.py - Public Domain Dictionary
 - scripts - CLI entrypoint
 - utils - code used by everything (e.g. romaji to kana conversion, regexes)

## JSONL (NameData)

Name information is collected in NameData python objects and serialised to and from JSONL
(JSON Lines) format. This is simply JSON except the file contains one JSON object per line,
and the object is serialised to only occupy one line (i.e. compact format).

There are several advantages to this format:
 1) As it is line based it is easy to split or aggregate the files, for example using `head`
    to test a script with a small number of inputs, or `parallel --pipe` to parallelise a
    script automatically, or `cat` to join inputs together.
 2) It can be filtered or queried using the `jq` tool, or in a pinch, `grep`.
 3) It is human readable

## Building the database

Run `make`.

## Running tests

Run `make test`.

For coverage run `make coverage`.
