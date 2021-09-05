from enum import Enum


class NameAuthenticity(Enum):
    """
    Represents the authenticity (realness) of name in a NameData.
    """

    """Real name"""
    REAL = 1
    """A pen name or geimei (artist name)"""
    PSEUDO = 2
    """A fictional character name"""
    FICTIONAL = 3

    def __repr__(self):
        return f"<{self.name.lower()}>"
