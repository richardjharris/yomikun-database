from yomikun.models import Lifetime


def test_lifetime_expand():
    a = Lifetime(1920, 1980)
    a.expand(Lifetime(1900, 2000))
    assert a == Lifetime(1900, 2000), 'expanded both'

    a = Lifetime(1920, 1980)
    a.expand(Lifetime(1930, 1970))
    assert a == Lifetime(1920, 1980), 'did not expand'

    a = Lifetime(1920, 1980)
    a.expand(Lifetime(1970, 1981))
    assert a == Lifetime(1920, 1981), 'expanded death'

    a = Lifetime(1920, 1980)
    a.expand(Lifetime(1919, 1950))
    assert a == Lifetime(1919, 1980), 'expanded (birth)'

    a = Lifetime(None, 2000)
    a.expand(Lifetime(3000, 3050))
    assert a == Lifetime(3000, 3050), 'None replaced (birth)'

    a = Lifetime(1920, None)
    a.expand(Lifetime(1900, 2000))
    assert a == Lifetime(1900, 2000), 'None replaced (death)'

    a = Lifetime(None, None)
    a.expand(Lifetime(1900, 2000))
    assert a == Lifetime(1900, 2000), 'None replaced (both)'


def test_lifetime_to_csv():
    assert Lifetime(1920, 1980).to_csv() == '1920-1980'
    assert Lifetime(None, 1980).to_csv() == '-1980'
    assert Lifetime(1920, None).to_csv() == '1920-'
    assert Lifetime(None, None).to_csv() == ''


def test_lifetime_to_dict():
    assert Lifetime(2001, 2040).to_dict() == {'birth_year': 2001, 'death_year': 2040}
