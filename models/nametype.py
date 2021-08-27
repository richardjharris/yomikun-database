from enum import Enum


class NameType(Enum):
    """
    Represents the type of name in a NameData.
    """

    """Real name"""
    REAL = 1
    """A pen name or geimei (artist name)"""
    PSEUDO = 2
    """A fictional character name"""
    FICTIONAL = 3
    """An additional name found with the real name, but a different person"""
    EXTRA = 4

    def __repr__(self):
        return f"<{self.name.lower()}>"
