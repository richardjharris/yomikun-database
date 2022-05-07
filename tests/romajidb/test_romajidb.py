from yomikun.romajidb.db import RomajiDB


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
