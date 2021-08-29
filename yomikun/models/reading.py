from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class Reading(DataClassJsonMixin):
    """
    The written (kaki) and read (yomi) form of a name part.
    """
    kaki: str
    yomi: str

    def __str__(self):
        return f"{self.kaki} ({self.yomi})"
