import pytest
from yomikun.models import NameData, NameAuthenticity


def test_add_tag():
    nd = NameData('高次', 'こうじ')
    nd.add_tag('foo')
    assert nd == NameData('高次', 'こうじ', tags={'foo'})

    nd.add_tag('bar')
    assert nd == NameData('高次', 'こうじ', tags={'foo', 'bar'})


def test_remove_tag():
    nd = NameData('高次', 'こうじ', tags={'foo', 'bar'})
    nd.remove_tag('foo')
    assert nd == NameData('高次', 'こうじ', tags={'bar'})


def test_remove_xx():
    nd = NameData(tags={'xx-romaji', 'xx-split', 'foo'})
    nd.remove_xx_tags()
    assert nd.tags == {'foo'}


def test_pos_validation():
    with pytest.raises(ValueError, match=r'^Data should be tagged'):
        NameData('愛', 'あい').validate()

    NameData('愛', 'あい', tags={'fem'}).validate()


def test_kaki_validation():
    nd = NameData.person('梅の里 昭二', 'うめのさと しょうじ')
    with pytest.raises(ValueError, match=r'^Invalid kaki'):
        nd.validate()

    nd.authenticity = NameAuthenticity.PSEUDO
    nd.validate()

    # Allow ノ as it is genuinely seen in names
    NameData.person('木ノ元 明博', 'きのもと あけひろ').validate()


def test_kana_validation():
    nd = NameData('心', 'ココロ', tags={'given'})
    with pytest.raises(ValueError, match=r'^Invalid yomi'):
        nd.validate()


def test_split():
    nd = NameData.person(
        '黒澤 明', 'くろさわ あきら', tags={'xx-romaji', 'masc'}, source='wikipedia_en'
    )
    sei, mei = nd.split()
    assert sei == NameData(
        '黒澤', 'くろさわ', tags={'xx-romaji', 'surname'}, source='wikipedia_en'
    )
    assert mei == NameData(
        '明', 'あきら', tags={'xx-romaji', 'masc'}, source='wikipedia_en'
    )

    # Errors
    with pytest.raises(ValueError, match=r'NameData must be a person'):
        NameData('明', 'あきら', tags={'masc'}).split()

    with pytest.raises(ValueError, match=r'NameData must not have any subreadings'):
        NameData(
            '黒澤 明',
            'くろさわ あきら',
            tags={'masc', 'person'},
            subreadings=[NameData('気　来', 'き き')],
        ).split()

    with pytest.raises(ValueError, match=r'NameData kaki is not split'):
        NameData('朱匠', 'しゅ たくみ', tags={'person'}).split()


def test_gender():
    assert NameData('まこと', 'まこと', tags={'fem'}).gender() == 'fem'
    assert NameData('まこと', 'まこと', tags={'masc'}).gender() == 'masc'
    assert NameData('まこと', 'まこと', tags={'fem', 'masc'}).gender() == 'fem'
    assert NameData('まこと', 'まこと').gender() is None
