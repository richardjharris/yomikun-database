from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Lifetime:
    """
    Represents a span of years lived. Both sides may be None
    (to either indicate unknown, or alive).
    """

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
