from __future__ import annotations
from typing import Iterable, TextIO
import collections
import logging
import jcconv3

import romkan

from yomikun.models import NameData
from yomikun.loader.aggregator import Aggregator
from yomikun.loader.models import NamePosition
from yomikun.utils.romaji import romaji_key

# TODO skip jmnedict ? - probably don't need to.
# #    could use 'dict' count as reference when picking 'canonical' values
# TODO use deduped people input?


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

            # XXX for some reason this contains katakana (maybe not anymore?)
            kana = jcconv3.kata2hira(kana)

            romkey = romaji_key(romkan.to_roma(kana))
            kaki = part.kaki
            pos = part.position.name

            data[(kaki, romkey, pos)].append(kana)

    # Try to pick one unique reading for the given kanji/romaji_key/part
    # This will be used for romaji conversion.
    for key in data.keys():
        values = data[key]
        counts = collections.Counter(values)
        unique = _find_unique_reading(key, counts, values)
        print(*key, unique or '', ','.join(sorted(counts.keys())), sep='\t')


def _find_unique_reading(key, counts, values):
    if len(counts) == 1:
        return values[0]
    else:
        top, = counts.most_common(1)
        if (top[1] / len(values)) >= 0.8:
            # Clear majority
            return top[0]
        else:
            # Not sure what to do
            logging.warning(
                f"No unique reading for {key} - too many values ({counts})")
            return
