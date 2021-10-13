from __future__ import annotations
from typing import Iterable, TextIO
import collections
import logging

import romkan

from yomikun.models import NameData
from yomikun.loader.aggregator import Aggregator
from yomikun.loader.models import NamePosition
from yomikun.utils.romaji import romaji_key

# TODO skip jmnedict ?


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
            romkey = romaji_key(romkan.to_roma(kana))
            kaki = part.kaki
            pos = part.position.name

            data[(kaki, romkey, pos)].append(kana)

    # Ensure there is only one sensible reading for a given kaki/romkey.
    for key in data.keys():
        values = data[key]
        uniq = collections.Counter(values)
        if len(uniq) == 1:
            print(*key, values[0], sep='\t')
        else:
            top, = uniq.most_common(1)
            if (top[1] / len(values)) >= 0.8:
                # Clear majority
                print(*key[0:3], top[0], sep='\t')
            else:
                # Not sure what to do
                logging.warning(
                    f"Skipping {key} - too many values ({uniq})")
                pass
