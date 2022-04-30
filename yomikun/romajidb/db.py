from __future__ import annotations
from dataclasses import dataclass, field
from typing import cast, Optional
import gzip
import os

import regex
import romkan
import jcconv3

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


def test_all_kana():
    db = RomajiDB()
    db.insert('佑祐', 'yusuke', 'mei', 'ゆうすけ')
    assert db.get('佑祐', 'yusuke', 'mei') == 'ゆうすけ'
    db.insert('齋藤', 'saito', 'sei', 'さいとう', {'さいと', 'さいとう'})
    assert db.get_all('齋藤', 'saito', 'sei') == (
        'さいとう',
        {'さいと', 'さいとう'},
    )
    assert db.get_all('齋藤', 'saito', 'mei') == (None, None)
    assert db.get_all('さいとう', 'saito', 'sei') == ('さいとう', {'さいとう'})
    assert db.get_all('マリン', 'marin', 'mei') == ('まりん', {'まりん'})
