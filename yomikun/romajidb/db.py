from __future__ import annotations

import gzip
import os
from dataclasses import dataclass, field
from typing import Optional, cast

import jcconv3
import regex
import romkan

from yomikun.utils.romaji.helpers import romaji_key

_INSTANCE = None


def romajidb() -> RomajiDB:
    """
    Returns a global RomajiDB object, instantiated only once per program.

    Loads 'data/romajidb.tsv.gz' from the current directory. Override with
    the ROMAJIDB_TSV_PATH environment variable.
    """
    global _INSTANCE
    if not _INSTANCE:
        path = os.environ.get('ROMAJIDB_TSV_PATH', 'data/romajidb.tsv.gz')
        _INSTANCE = RomajiDB.load(path)
    return _INSTANCE


RomajiDbKey = tuple[str, str, str]
RomajiDbResult = tuple[Optional[str], Optional[set[str]]]


@dataclass
class RomajiDB:
    data: dict[RomajiDbKey, RomajiDbResult] = field(
        default_factory=dict, repr=False, compare=False
    )

    @staticmethod
    def load(file: str):
        db = RomajiDB()

        with gzip.open(file, mode='rt') as fh:
            for line in fh:
                values = line.rstrip().split('\t')
                kanji, romkey, part, main_kana, all_kana = values

                # Convert all_kana from csv to set
                all_kana = set(','.split(all_kana))

                db.insert(kanji, romkey, part, main_kana, all_kana)
        return db

    def insert(
        self,
        kanji: str,
        romkey: str,
        part: str,
        main_kana: str,
        all_kana: set[str] | None = None,
    ):
        if all_kana is None:
            all_kana = set(main_kana)

        self.data[(kanji, romkey, part)] = (main_kana, all_kana)

    def get_all(self, kanji: str, romkey: str, part: str) -> RomajiDbResult:
        # Check if the kanji is actually just the romaji in kana
        # or katakana form, if so, return it.
        if not regex.match(r'\p{Han}', kanji):
            if romaji_key(romkan.to_roma(kanji)) == romkey:
                kana = cast(str, jcconv3.kata2hira(kanji))
                return (kana, set([kana]))

        return self.data.get((kanji, romkey, part), (None, None))

    def get(self, kanji: str, romkey: str, part: str) -> str | None:
        return self.get_all(kanji, romkey, part)[0]
