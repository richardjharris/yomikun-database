"""
Reads JMNEdict file and extracts full names + lifetimes as well
as individual surnames and given names.

The JMNEdict is extremely comprehensive, but this causes problems - it contains
extremely rare readings, made-up names, and the name type is often incorrect.
For example many names are marked up as both a given name and a surname despite this
being very rare in Japanese.

Our strategy here is to import all of it, then use Wikipedia and other data to
identify the readings that are actually seen in the real world. For this reason we
also import 'unclass'-type names that are not confirmed to be person names at all.
These would show up dead last in a dictionary lookup, but are good for completeness.
"""

from __future__ import annotations
import logging
import os
import sys
import json

import jamdict

import yomikun.jmnedict

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

jam = jamdict.Jamdict(
    memory_mode=False,
)
assert jam.has_jmne()

# Jamdict requires pos to be non-empty but it is ignored for name queries
result = jam.lookup_iter('%', pos=['dummy'])
for name in result.names:
    data = name.to_dict()
    try:
        for output in yomikun.jmnedict.parse(data):
            print(json.dumps(output, ensure_ascii=False))
    except KeyboardInterrupt:
        print("caught INT, exiting", file=sys.stderr)
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(0)
    except Exception as err:
        logging.exception(f"Failed to parse entry")
        logging.info(data)
