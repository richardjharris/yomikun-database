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
