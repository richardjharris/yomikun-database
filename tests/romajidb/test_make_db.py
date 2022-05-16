from io import StringIO

from yomikun.models.name_position import NamePosition
from yomikun.models.namedata import NameData
from yomikun.romajidb.make import make_romajidb


def test_make_romajidb():
    input_data = [
        NameData.person('後藤 美優', 'ごとう みゆ'),
        # Include multiple copies of みゆう so there is a clear majority (>80%)
        NameData('美優', 'みゆう', position=NamePosition.mei),
        NameData('美優', 'みゆう', position=NamePosition.mei),
        NameData('美優', 'みゆう', position=NamePosition.mei),
        NameData('美優', 'みゆう', position=NamePosition.mei),
        NameData.person('辻 美優', 'つじ みゆう'),
        # This entry should be ignored as it was parsed from the romaji 'goto'
        NameData('後藤', 'ごと', position=NamePosition.mei, tags={'xx-romaji'}),
        # This reading has no clear majority
        NameData('優凛', 'ゆうりん', position=NamePosition.mei),
        NameData('優凛', 'ゆりん', position=NamePosition.mei),
        # This will be ignored as unknown
        NameData('田中', 'たなか', position=NamePosition.unknown),
    ]
    output = StringIO()

    make_romajidb(input_data, db_out=output)

    expected_lines = {
        "後藤\tgoto\tsei\tごとう\tごとう",  # ごと ignored
        "美優\tmiyu\tmei\tみゆう\tみゆ,みゆう",  # みゆう more common
        "辻\ttsuji\tsei\tつじ\tつじ",
        "優凛\tyurin\tmei\t\tゆうりん,ゆりん",
    }

    actual_lines = set(output.getvalue().splitlines())

    assert actual_lines == expected_lines
