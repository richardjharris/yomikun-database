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

For more information, see the docs/ directory.

## Building the database

Run `make`.

## Running tests

Run `make test`.

For coverage run `make cover`.
