import regex

from yomikun.utils import patterns


def test_sei():
    expect_match = [
        "江戸",
        "江戸山",
        "三ツ木",
        "木ノ本",
        "茂り松",
        "回り道",
        "廻り道",
        "見ル野",
        "賀シ尾",
        "一の瀬",
        "一ノ瀬",
    ]

    expect_fail = [
        "ひらがな",
        "えの島",
    ]

    for sei in expect_match:
        assert regex.match(fr'^{patterns.sei_pat}$', sei)

    for sei in expect_fail:
        assert not regex.match(fr'^{patterns.sei_pat}$', sei)
