from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Lifetime():
    """
    Represents a span of years lived. Both sides may be None
    (to either indicate unknown, or alive).
    """
    # TODO distinguish unknown and alive?
    birth_year: int | None = None
    death_year: int | None = None

    def __bool__(self):
        return self.birth_year is not None or \
            self.death_year is not None

    def __repr__(self):
        return f"<{self.birth_year or ''} ~ {self.death_year or ''}>"

    def merge_in(self, other: Lifetime):
        """
        Fill missing data with data from another object.
        """
        # TODO if the other object is complete and we aren't, really
        #      we should prefer the other object? Do we want to ensure
        #      the other data matches first?
        if self.birth_year is None:
            self.birth_year = other.birth_year
        if self.death_year is None:
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
