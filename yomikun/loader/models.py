from __future__ import annotations

import enum


class Gender(enum.Enum):
    unknown = 1
    male = 2
    female = 3
    neutral = 4


class NamePosition(enum.Enum):
    unknown = 1
    sei = 2
    mei = 3
