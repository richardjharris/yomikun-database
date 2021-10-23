"""
Import data from ResearchMap user cards
"""
import logging
import os
import sys
import time

from yomikun.researchmap import parse_researchmap

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

parsed, errors, total = 0, 0, 0
start_time = time.monotonic()

for line in sys.stdin:
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
        logging.error(f"Failed to validate {parts}: {e}")
        errors += 1
    except Exception:
        logging.exception(f'Error when parsing {parts}')
        sys.exit(1)
    total += 1

elapsed = time.monotonic() - start_time

print(
    f'Parsed {parsed} of {total} results ({parsed/total:.1%}) in {elapsed:.0f}s ({errors} errors)',
    file=sys.stderr)
