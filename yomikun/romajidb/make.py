from __future__ import annotations

import collections
import logging
from typing import Iterable, TextIO

import jcconv3
import romkan

from yomikun.loader.aggregator import Aggregator
from yomikun.models import NameData, NamePosition
from yomikun.utils.romaji.helpers import romaji_key


def make_romajidb(names: Iterable[NameData], db_out: TextIO):
    data = collections.defaultdict(list)

    for name in names:
        if 'xx-romaji' in name.tags:
            continue

        logging.debug(f"Name: {name}")

        Aggregator.copy_data_to_subreadings(name)
        for part, gender in Aggregator.extract_name_parts(name):
            logging.info(f"Part {part} gender={gender}")
            if part.position == NamePosition.unknown:
                continue

            # Generate romaji key
            kana = part.yomi

            # Handle katakana just in case any is present
            kana = jcconv3.kata2hira(kana)

            romkey = romaji_key(romkan.to_roma(kana))
            kaki = part.kaki
            pos = part.position.name

            data[(kaki, romkey, pos)].append(kana)

    # Try to pick one unique reading for the given kanji/romaji_key/part
    # This will be used for romaji conversion.
    for key, values in data.items():
        counts = collections.Counter(values)
        unique = _find_unique_reading(key, counts, values)
        print(
            *key, unique or '', ','.join(sorted(counts.keys())), sep='\t', file=db_out
        )


def _find_unique_reading(key, counts, values):
    if len(counts) == 1:
        return values[0]
    else:
        (top,) = counts.most_common(1)
        if (top[1] / len(values)) >= 0.8:
            # Clear majority
            return top[0]
        else:
            # Not sure what to do
            logging.warning(f"No unique reading for {key} - too many values ({counts})")
            return
