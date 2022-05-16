## Contributor guidelines

Send a pull request, ideally with tests!

### Coding conventions

* Python 3.10+
* Use type hinting where possible
* Four spaces, soft tabs (see `.editorconfig`)
* Auto-format code with Black and typecheck with Pylance, linted with flake8.
 - Run `make pylint` to run pylint lints, which are a bit noisier
* Run `make isort` to keep imports sorted
* Each file should have a test in the `tests` directory, following the same
  structure as the `yomikun` directory.
 - Alternately add a testcase to `tests/commands/testcases`.
* Add requirements to `requirements.txt` and dev-only requirements to
  `requirements-dev.txt`.

### Imports

Python has several ways to import things. The following scheme is suggested:

1. Use `import module` if the module name is short, or used only a few times
2. Use `import long.module as x` if the module name is long 
3. Use `from module import x` where it is idiomatic to do so: `dataclasses`, `typing`, `datetime` etc.

Rationale: it should be obvious where functions come from, but not at a large
cost to readability.

### Prerequisites

Code: Python 3.10+, the modules in `requirements.txt` (and `requirements-dev.txt`
for development). See the `prep*` makefile targets.

Makefile: a Linux-compatible environment with `moreutils` (`parallel` tool),
`pzcat` (to be added). For fast conversion of MediaWiki XML dumps to JSON,
Perl and the `MediaWiki::DumpFile::FastPages` module is used. If you don't
want to use Perl, you can do the conversion yourself quite easily.

At present I use several personal data sources to generate the name database,
so the makefile will not run as-is. To build a simple version, you can remove
any data sources that won't build, and provide `enwiki.xml.bz2` and `jawiki.xml.bz2`
from Mediawiki dumps.
