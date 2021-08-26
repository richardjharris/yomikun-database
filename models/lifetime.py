from __future__ import annotations

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Lifetime:
    """
    Represents a span of years lived. Both sides may be None
    (to either indicate unknown, or alive).
    """
    # TODO distinguish unknown and alive.
    birth_year: int | None = None
    death_year: int | None = None

    def __bool__(self):
        return self.birth_year is not None or \
            self.death_year is not None

    def __str__(self):
        return f"{self.birth_year or ''} ~ {self.death_year or ''}"
