from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import cast

import regex
import romkan
import jcconv3
import gzip

from yomikun.utils.romaji import romaji_key


instance = None


def romajidb():
    """
    Returns a global RomajiDB object, instantiated only once per program.

    Loads 'data/romajidb.tsv.gz' from the current directory. Override with
    ROMAJIDB_TSV_PATH
    """
    global instance
    if not instance:
        path = os.environ.get('ROMAJIDB_TSV_PATH', 'data/romajidb.tsv.gz')
        instance = RomajiDB.load(path)
    return instance


@dataclass
class RomajiDB():
    data: dict[tuple[str, str, str], str] = field(
        default_factory=dict, repr=False, compare=False)

    @staticmethod
    def load(file: str):
        db = RomajiDB()

        with gzip.open(file, mode='rt') as fh:
            for line in fh:
                values = line.rstrip().split('\t')
                db.insert(*values)
        return db

    def insert(self, kanji: str, romkey: str, part: str, kana: str):
        self.data[(kanji, romkey, part)] = kana

    def get(self, kanji: str, romkey: str, part: str) -> str | None:
        # Check if the kanji is actually just the romaji in kana
        # or katakana form, if so, return it.
        if not regex.match(r'\p{Han}', kanji):
            if romaji_key(romkan.to_roma(kanji)) == romkey:
                return cast(str, jcconv3.kata2hira(kanji))

        return self.data.get((kanji, romkey, part), None)


def test_basic():
    db = RomajiDB()
    db.insert('佑祐', 'yusuke', 'mei', 'ゆうすけ')
    assert db.get('佑祐', 'yusuke', 'mei') == 'ゆうすけ'
    assert db.get('佑祐', 'yusuke', 'sei') is None
    assert db.get('諭助', 'yusuke', 'mei') is None
    assert db.get('佑祐', 'musuke', 'mei') is None

    db.insert('諭助', 'yusuke', 'mei', 'ゆすけ')
    assert db.get('諭助', 'yusuke', 'mei') == 'ゆすけ'


def test_kana():
    db = RomajiDB()  # empty
    assert db.get('あきら', 'akira', 'mei') == 'あきら'
    assert db.get('ココロ', 'kokoro', 'mei') == 'こころ'
