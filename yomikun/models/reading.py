from dataclasses import dataclass


@dataclass
class Reading():
    """
    The written (kaki) and read (yomi) form of a name part.
    """
    kaki: str
    yomi: str

    def __str__(self):
        return f"{self.kaki} ({self.yomi})"
