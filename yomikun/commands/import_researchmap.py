import logging
import sys

import click

from yomikun.researchmap import parse_researchmap
from yomikun.utils.timer import Timer


@click.command()
@click.argument('input', type=click.File('r'), default='-')
def import_researchmap(input):
    """
    Import data from ResearchMap user cards

    Generates a JSONL file with one row per name; this data should be
    anonymised via `yomikun split-names` before being used.
    """
    parsed, errors, total = 0, 0, 0
    timer = Timer()

    for line in input:
        line = line.rstrip()
        parts = line.split('\t')
        try:
            if len(parts) < 2:
                # There are a few dozen records with 0/1 name parts. They're not
                # useful to us as there is no reading.
                continue

            kana = parts[0]
            kanji = parts[1]
            english = parts[2] if len(parts) == 3 else ''

            if data := parse_researchmap(kana, kanji, english):
                print(data.to_jsonl())
                parsed += 1
        except NotImplementedError:
            logging.error(f"Failed to parse {parts}", exc_info=True)
            logging.error('-----')
            errors += 1
        except ValueError as e:
            logging.error(f"Failed to validate {parts}: {e}", exc_info=True)
            errors += 1
        except Exception:
            logging.exception(f'Error when parsing {parts}')
            sys.exit(1)
        total += 1

    click.echo(
        f'Parsed {parsed} of {total} results ({parsed/total:.1%}) '
        f'in {timer.elapsed}s ({errors} errors)',
        err=True,
    )
