from __future__ import annotations
from dataclasses import dataclass, field

instance = None


def romajidb():
    """
    Returns a global RomajiDB object, instantiated only once per program.

    Loads 'romajidb.tsv' from the current directory.
    """
    global instance
    if not instance:
        instance = RomajiDB.load('data/romajidb.tsv')
    return instance


@dataclass
class RomajiDB():
    data: dict[tuple[str, str, str], str] = field(default_factory=dict)

    @staticmethod
    def load(file: str):
        db = RomajiDB()

        with open(file) as fh:
            for line in fh:
                values = line.strip().split('\t')
                db.insert(*values)
        return db

    def insert(self, kanji: str, romaji_key: str, part: str, kana: str):
        self.data[(kanji, romaji_key, part)] = kana

    def get(self, kanji: str, romaji_key: str, part: str) -> str | None:
        return self.data.get((kanji, romaji_key, part), None)


def test_basic():
    db = RomajiDB()
    db.insert('佑祐', 'yusuke', 'mei', 'ゆうすけ')
    assert db.get('佑祐', 'yusuke', 'mei') == 'ゆうすけ'
    assert db.get('佑祐', 'yusuke', 'sei') is None
    assert db.get('諭助', 'yusuke', 'mei') is None
    assert db.get('佑祐', 'musuke', 'mei') is None

    db.insert('諭助', 'yusuke', 'mei', 'ゆすけ')
    assert db.get('諭助', 'yusuke', 'mei') == 'ゆすけ'
