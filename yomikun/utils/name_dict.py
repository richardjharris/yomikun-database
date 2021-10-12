"""
Name dictionary based on JMnedict (may include our own
data in the future).
"""
from dataclasses import dataclass
import logging

import jamdict

# TODO: turn on memory_mode outside of test mode (??)
# TODO: we use jamdict-data for now
jam = jamdict.Jamdict(
    memory_mode=False,
)
assert jam.has_jmne()

NOISY_LOGGERS = ('jamdict.jmdict_sqlite',
                 'jamdict.jmnedict_sqlite',
                 'puchikarui.puchikarui')

for logger in NOISY_LOGGERS:
    logging.getLogger(logger).setLevel(logging.ERROR)


@dataclass
class NameResult:
    kana: list[str]
    kanji: list[str]


class NameDict():
    @classmethod
    def find(cls, query, senses) -> list[NameResult]:
        """
        Given kana or kanji name (`query`), return all results matching the
        senses in `senses`.
        """
        result = jam.lookup(
            query=query, strict_lookup=True, lookup_chars=False)
        out = []
        for name in result.names:
            name_senses = cls._get_sense_names(name.senses)
            if name_senses.intersection(senses):
                out.append(NameResult(
                    kana=[kf.text for kf in name.kana_forms],
                    kanji=[kf.text for kf in name.kanji_forms],
                ))
        return out

    @classmethod
    def find_surname(cls, query):
        return cls.find(query, senses=['surname'])

    @classmethod
    def find_given_name(cls, query):
        return cls.find(query, senses=['masc', 'fem', 'given'])

    @classmethod
    def all_data(cls):
        """
        Return all name entries as raw python dictionary data.
        """
        # Jamdict requires pos to be non-empty but it is ignored for name queries
        results = jam.lookup_iter('%', pos=['dummy'])
        for name in results.names:
            yield name.to_dict()

    @staticmethod
    def _get_sense_names(senses: list) -> set[str]:
        names = set()
        for sense in senses:
            for name_type in sense.name_type:
                names.add(name_type)
        return names
