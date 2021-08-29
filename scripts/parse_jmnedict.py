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
from operator import itemgetter
import os
import sys
import re
import json
from dataclasses import dataclass, field

import romkan
import jamdict

from models import Lifetime
from utils.split import split_kanji_name

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

jam = jamdict.Jamdict(
    memory_mode=False,
)
assert jam.has_jmne()

name_types_we_want = {'fem', 'given', 'person', 'masc', 'surname', 'unclass'}


@dataclass
class JmneGloss:
    # Match a YYYY.MM.DD date and capture the year
    DATE_PAT = r'(\d{3,4})(?:\.\d\d?(?:\.\d\d?)?)?'
    # Match (date-date) or (date-)
    DATE_SPAN_PAT = re.compile(fr'\({DATE_PAT}-(?:{DATE_PAT})?\)$')
    NAME_PAT = re.compile(r'^(\w+ \w+)')

    name: str | None = None
    lifetime: Lifetime = field(default_factory=Lifetime)
    source_string: str | None = None

    @classmethod
    def parse_from_sense(cls, sense) -> JmneGloss:
        """Parse English gloss from a Sense object"""
        for gloss in sense['SenseGloss']:
            if gloss['lang'] == 'eng':
                return cls.parse(gloss['text'])

        return JmneGloss()

    @classmethod
    def parse(cls, gloss: str) -> JmneGloss:
        obj = JmneGloss(source_string=gloss)

        if m := re.search(cls.DATE_SPAN_PAT, gloss):
            birth, death = m.groups()
            obj.lifetime = Lifetime(int(birth), int(
                death) if death else None)

        if m := re.match(r'^(\w+ \w+)', gloss):
            obj.name = m[1]

        return obj


def parse(data: dict):
    for sense in data['senses']:
        name_types = set(sense['name_type']).intersection(
            name_types_we_want)
        if not name_types:
            return

        if 'person' in name_types:
            # Extract lifetime if available
            gloss = JmneGloss.parse_from_sense(sense)
        else:
            gloss = JmneGloss()

        for kanji in map(itemgetter('text'), data['kanji']):
            for kana in map(itemgetter('text'), data['kana']):
                if gloss.name:
                    # Convert name to hiragana and use it to split the name
                    split_kana = romkan.to_hiragana(gloss.name)
                    split_kanji = split_kanji_name(kanji, split_kana)
                    if kanji != split_kanji:
                        kanji, kana = split_kanji, split_kana

                output = {
                    'kaki': kanji,
                    'yomi': kana,
                    'tags': list(name_types),
                    'orig': gloss.source_string,
                }
                if gloss.lifetime:
                    output['lifetime'] = gloss.lifetime.to_dict()
                print(json.dumps(output, ensure_ascii=False))


# Jamdict requires pos to be non-empty but it is ignored for name queries
result = jam.lookup_iter('%', pos=['dummy'])
for name in result.names:
    data = name.to_dict()

    # TODO this does not always shut down tidily on Ctrl+C
    try:
        parse(data)
    except KeyboardInterrupt:
        print("caught INT, exiting", file=sys.stderr)
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(0)
    except Exception as err:
        logging.error(f"Failed to parse entry: {err!r}")
        logging.info(data)
