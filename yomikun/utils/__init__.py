import regex


def normalise_whitespace(s: str) -> str:
    """Trim and normalise whitespace in a string"""
    s = s.strip()
    s = regex.sub(r'\s+', ' ', s)
    return s


def test_normalise_whitespace():
    assert normalise_whitespace(' foo ') == 'foo'
    assert normalise_whitespace('A   B') == 'A B'
    assert normalise_whitespace('亜　美') == '亜 美'
