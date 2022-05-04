"""
Name dictionary based on JMnedict (may include our own
data in the future).
"""
from dataclasses import dataclass
import logging
import jamdict

from yomikun.romajidb.db import romajidb
from yomikun.utils.romaji.helpers import romaji_key

jam = jamdict.Jamdict(memory_mode=False)
assert jam.has_jmne()

NOISY_LOGGERS = (
    'jamdict.jmdict_sqlite',
    'jamdict.jmnedict_sqlite',
    'puchikarui.puchikarui',
)

for logger in NOISY_LOGGERS:
    logging.getLogger(logger).setLevel(logging.ERROR)


@dataclass
class NameResult:
    kana: list[str]
    kanji: list[str]


def match_name(kanji, kana, sei: bool, romaji=False):
    if romaji:
        romkey = romaji_key(kana)
        part = 'sei' if sei else 'mei'
        result = romajidb().get(kanji, romkey, part)
        if result:
            return True
    else:
        if sei:
            results = find_surname(kanji)
        else:
            results = find_given_name(kanji)

        for result in results:
            if kana in result.kana:
                return True

    return False


def find(query, senses) -> list[NameResult]:
    """
    Given kana or kanji name (`query`), return all results matching the
    senses in `senses`.
    """
    result = jam.lookup(query=query, strict_lookup=True, lookup_chars=False)
    out = []
    for name in result.names:
        name_senses = _get_sense_names(name.senses)
        if name_senses.intersection(senses):
            out.append(
                NameResult(
                    kana=[kf.text for kf in name.kana_forms],
                    kanji=[kf.text for kf in name.kanji_forms],
                )
            )
    return out


def find_surname(query):
    return find(query, senses=['surname'])


def find_given_name(query):
    return find(query, senses=['masc', 'fem', 'given'])


def all_jmnedict_data():
    """
    Return all name entries as raw python dictionary data.
    """
    # Jamdict requires pos to be non-empty but it is ignored for name queries
    results = jam.lookup_iter('%', pos=['dummy'])
    for name in results.names:
        yield name.to_dict()


def _get_sense_names(senses: list) -> set[str]:
    names = set()
    for sense in senses:
        for name_type in sense.name_type:
            names.add(name_type)
    return names
