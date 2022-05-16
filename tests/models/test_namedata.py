import pytest

from yomikun.models import Lifetime, NameAuthenticity, NameData
from yomikun.models.gender import Gender
from yomikun.models.name_position import NamePosition


def test_unknown_validation():
    with pytest.raises(ValueError, match=r'^name with position=unknown'):
        NameData('愛', 'あい', position=NamePosition.unknown).validate()

    NameData('愛', 'あい', position=NamePosition.mei, gender=Gender.female).validate()


def test_kaki_validation():
    nd = NameData.person('foobar', 'うめのさと しょうじ')
    with pytest.raises(ValueError, match=r'^Invalid kaki'):
        nd.validate()

    nd.authenticity = NameAuthenticity.PSEUDO
    nd.validate()

    # Allow ノ as it is genuinely seen in names
    NameData.person('木ノ元 明博', 'きのもと あけひろ').validate()


def test_kana_validation():
    nd = NameData('心', 'ココロ', position=NamePosition.mei)
    with pytest.raises(ValueError, match=r'^Invalid yomi'):
        nd.validate()


def test_split():
    nd = NameData.person(
        '黒澤 明',
        'くろさわ あきら',
        tags={'xx-romaji'},
        gender=Gender.male,
        source='wikipedia_en',
    )
    sei, mei = nd.split()
    assert sei == NameData(
        '黒澤',
        'くろさわ',
        tags={'xx-romaji'},
        position=NamePosition.sei,
        source='wikipedia_en',
    )
    assert mei == NameData(
        '明',
        'あきら',
        tags={'xx-romaji'},
        position=NamePosition.mei,
        gender=Gender.male,
        source='wikipedia_en',
    )

    # Errors
    with pytest.raises(ValueError, match=r'NameData must be a person'):
        NameData('明', 'あきら', gender=Gender.male).split()

    with pytest.raises(ValueError, match=r'NameData must not have any subreadings'):
        NameData.person(
            '黒澤 明',
            'くろさわ あきら',
            gender=Gender.male,
            subreadings=[NameData('気　来', 'き き')],
        ).split()

    with pytest.raises(ValueError, match=r'NameData kaki is not split'):
        NameData.person('朱匠', 'しゅ たくみ').split()


def test_copy_data_to_subreadings():
    nd = NameData.person(
        '夏目 漱石',
        'なつめ そうせき',
        lifetime=Lifetime(1867, 1916),
        source='wikipedia_en',
        subreadings=[
            NameData('夏目 金之助', 'なつめ きんのすけ', authenticity=NameAuthenticity.REAL)
        ],
        authenticity=NameAuthenticity.PSEUDO,
    )

    nd.clean()

    assert nd.subreadings[0].lifetime == Lifetime(1867, 1916)
    assert nd.subreadings[0].source == 'wikipedia_en'


def test_from_csv_regression():
    row = {
        'kaki': '小田　剛嗣',
        'yomi': 'おだ つよし',
        'tags': 'm',
        'lifetime': '1920-1980',
        'notes': '',
    }
    result = NameData.from_csv(row)
    assert result == NameData.person(
        '小田　剛嗣', 'おだ つよし', gender=Gender.male, lifetime=Lifetime(1920, 1980)
    )
