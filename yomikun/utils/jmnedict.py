"""
Interface to the JMnedict database. This is a comprehensive but somewhat
noisy database of Japanese names, which is used as a data source and
also sometimes consulted when splitting names.
"""
import logging
from dataclasses import dataclass
from typing import Any, Generator

import jamdict

# Jamdict and its deps are quite noisy and the logs are not relevant to us.
NOISY_LOGGERS = (
    'jamdict.jmdict_sqlite',
    'jamdict.jmnedict_sqlite',
    'puchikarui.puchikarui',
)

_instance = None


def jam() -> jamdict.Jamdict:
    """
    Returns a global JamDict object, instantiated only once per program.

    Loads a local copy of the database via the jamdict-data module.
    """
    global _instance
    if not _instance:
        _instance = jamdict.Jamdict(memory_mode=False)
        assert _instance.has_jmne()

        for logger in NOISY_LOGGERS:
            logging.getLogger(logger).setLevel(logging.ERROR)

    return _instance


@dataclass
class NameResult:
    kana: list[str]
    kanji: list[str]


def find(query: str, senses) -> list[NameResult]:
    """
    Given kana or kanji name (`query`), return all results matching the
    senses in `senses`.
    """
    result = jam().lookup(query=query, strict_lookup=True, lookup_chars=False)
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


def find_surname(query: str):
    """
    Returns surnames precisely matching `query`.
    """
    return find(query, senses=['surname'])


def find_given_name(query: str):
    """
    Returns given names precisely matching `query`.
    """
    return find(query, senses=['masc', 'fem', 'given'])


def all_jmnedict_data() -> Generator[dict[str, Any], None, None]:
    """
    Return all name entries as raw python dictionary data.
    """
    # Jamdict requires pos to be non-empty but it is ignored for name queries
    results = jam().lookup_iter('%', pos=['dummy'])
    for name in results.names:
        yield name.to_dict()


def _get_sense_names(senses: list) -> set[str]:
    names = set()
    for sense in senses:
        for name_type in sense.name_type:
            names.add(name_type)
    return names
