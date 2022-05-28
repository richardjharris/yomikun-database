"""
Test that the final DB generation code is working, using a small input set.
"""
import sqlite3
from io import StringIO
from tempfile import NamedTemporaryFile

from yomikun.sqlite import builder
from yomikun.sqlite.models.name_part import NamePart

MEI = NamePart.mei.value
SEI = NamePart.sei.value


def test_sqlite_builder():
    input_data = """
{"hits_male": 0, "hits_female": 0, "hits_unknown": 3, "years_seen": {"birth_year": 1986, "death_year": null}, "hits_xx_romaji": 0, "hits_pseudo": 0, "hits_total": 3, "kaki": "雫", "yomi": "しずく", "part": "sei", "ml_score": 153, "ct_score": 1.0, "ct_confidence": 0.7430708254900826}
{"hits_male": 0, "hits_female": 7, "hits_unknown": 1, "years_seen": {"birth_year": 1984, "death_year": null}, "hits_xx_romaji": 0, "hits_pseudo": 2, "hits_total": 8, "kaki": "雫", "yomi": "しずく", "part": "mei", "ml_score": 153, "ct_score": 1.0, "ct_confidence": 0.7430708254900826}
{"hits_male": 0, "hits_female": 0, "hits_unknown": 4449, "years_seen": {"birth_year": 1501, "death_year": 2021}, "hits_xx_romaji": 77, "hits_pseudo": 90, "is_top5k": true, "population": 1346000, "hits_total": 4449, "kaki": "田中", "yomi": "たなか", "part": "sei", "ml_score": 16, "ct_score": -1.0, "ct_confidence": 0.2054964498186217}
    """.strip()  # noqa

    expected_names = [
        # kaki, yomi, part, hits_total, hits_male, hits_female, hits_pseudo, female_ratio
        ("雫", "shizuku", SEI, 3, 0, 0, 0, 153),
        ("雫", "shizuku", MEI, 8, 0, 7, 2, 153),
        ("田中", "tanaka", SEI, 4449, 0, 0, 90, 16),
    ]

    expected_kanji_stats = [
        # kaki, part, gender, hits_total, female_ratio
        ('中', SEI, 'A', 4449, 127),
        ('田', SEI, 'A', 4449, 127),
        ('雫', SEI, 'A', 3, 127),
        ('雫', MEI, 'A', 8, 255),
        ('雫', MEI, 'F', 7, 0),  # TODO should be 255?
        ('雫', MEI, 'M', 0, 0),
    ]

    expected_quiz = [
        # kaki, part, yomi, total
        # Shizuku not included -- too small
        ('田中', SEI, 'tanaka', 4449),
    ]

    with NamedTemporaryFile(suffix='.db') as dbfile:
        connection = sqlite3.connect(dbfile.name)
        builder.build_sqlite(connection, StringIO(input_data))

        # Test the DB contents
        cursor = connection.cursor()

        _test_table(
            cursor,
            'names',
            expected_names,
            'SELECT * FROM names ORDER BY yomi, kaki, part',
        )
        _test_table(
            cursor,
            'kanji_stats',
            expected_kanji_stats,
            'SELECT * FROM kanji_stats ORDER BY kanji, part, gender',
        )
        _test_table(
            cursor,
            'quiz',
            expected_quiz,
            'SELECT * FROM quiz ORDER BY kaki, part, yomi',
        )


def _test_table(cursor, table_name, expected, query):
    cursor.execute(query)
    actual = cursor.fetchall()
    assert actual == expected, f'table {table_name}'
    pass
