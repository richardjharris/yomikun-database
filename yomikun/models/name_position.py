import enum


class NamePosition(enum.Enum):
    """Position of a name within a full name, or 'person' for a full name."""

    unknown = 1
    sei = 2
    mei = 3
    person = 4
