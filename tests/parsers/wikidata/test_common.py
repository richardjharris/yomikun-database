import pytest

from yomikun.parsers.wikidata.common import extract, year


def test_extract():
    mydict = {
        'foo': {
            'bar': 'hello',
            'baz': 'world',
            'number': 5.0,
        },
        'bar': 'blah',
    }
    assert extract(mydict, 'foo.bar') == 'hello'
    assert extract(mydict, 'bar') == 'blah'
    assert extract(mydict, 'foo.baz') == 'world'
    assert extract(mydict, 'foo.nonexist') is None

    with pytest.raises(AssertionError):
        extract(mydict, 'foo.number')

    with pytest.raises(TypeError):
        extract(mydict, 'foo.bar.baz')  # tries to index a string


def test_year():
    assert year('2019-01-01') == 2019
    assert year('2019') == 2019
    assert year('tBnodeInfo') is None
    assert year(None) is None
