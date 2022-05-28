from yomikun.sqlite.models.name_part import NamePart


def test_name_part():
    assert NamePart(1).name == 'sei'
    assert NamePart['mei'].value == 2

    assert NamePart.mei.kanji == '名'
    assert NamePart.sei.kanji == '姓'
    assert NamePart.person.kanji == '人'
    assert NamePart.unknown.kanji == '？'
