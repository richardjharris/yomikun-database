from pathlib import Path
from yomikun.gender.dict import GenderDict, GenderInfo

FIXTURE_DIR = Path(__file__).parent.joinpath('fixtures')


def test_basic_dict():
    dict_path = FIXTURE_DIR.joinpath('gender-dict-sample.jsonl')
    gd = GenderDict(str(dict_path))
    makoto = gd.lookup('真', 'まこと')
    assert makoto is not None
    assert makoto == GenderInfo(-2, -0.8, 0.95)
    assert makoto.to_dict() == {
        'ml_score': -2,
        'ct_score': -0.8,
        'ct_confidence': 0.95,
    }

    assert gd.lookup('真琴', 'まこと') == GenderInfo(0.5, -0.8, 0.95)
    assert gd.lookup('真', 'ばなな') is None
    assert gd.lookup('場', 'まこと') is None
    assert gd.lookup('淳', 'ひろし') == GenderInfo(-6, -0.99, 0.99)
