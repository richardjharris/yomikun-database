from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Lifetime:
    """
    Represents a span of years lived. Both sides may be None
    (to either indicate unknown, or alive).
    """

    # TODO distinguish unknown and alive?
    birth_year: int | None = None
    death_year: int | None = None

    def __bool__(self):
        return self.birth_year is not None or self.death_year is not None

    def __repr__(self):
        return f"<{self.birth_year or ''} ~ {self.death_year or ''}>"

    def expand(self, other: Lifetime):
        """
        Expand this lifetime so it uses `other`'s birth_year if it is earlier than
        this one, and `other`'s death_year if it is later.
        """
        if self.birth_year is None or (
            other.birth_year is not None and self.birth_year > other.birth_year
        ):
            self.birth_year = other.birth_year

        if self.death_year is None or (
            other.death_year is not None and self.death_year < other.death_year
        ):
            self.death_year = other.death_year

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_string(cls, value: str):
        lifetime = Lifetime()
        birth, death = value.split('~')
        if len(birth.strip()):
            lifetime.birth_year = int(birth)
        if len(death.strip()):
            lifetime.death_year = int(death)

        return lifetime

    def to_csv(self) -> str:
        if not self:
            return ''

        birth = str(self.birth_year) if self.birth_year else ''
        death = str(self.death_year) if self.death_year else ''
        return f"{birth}-{death}"


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
