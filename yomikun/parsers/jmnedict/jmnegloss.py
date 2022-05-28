from __future__ import annotations

import re
from dataclasses import dataclass, field

from yomikun.models.lifetime import Lifetime


@dataclass
class JmneGloss:
    """
    Parses a JMNEdict gloss (a person name and lifetime) and exposes the results.
    """

    # Match a YYYY.MM.DD date and capture the year
    DATE_PAT = r"(\d{3,4})(?:\.\d\d?(?:\.\d\d?)?|[?]|)"

    # Match (date-date) or (date-)
    # some are like 'Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)' so
    # we also match on a preceding comma.
    DATE_SPAN_PAT = re.compile(rf"[\(, ]{DATE_PAT}-(?:{DATE_PAT})?\)")

    name: str | None = None
    lifetime: Lifetime = field(default_factory=Lifetime)
    source_string: str | None = None

    @classmethod
    def parse_from_sense(cls, sense) -> JmneGloss:
        """Parse English gloss from a Sense object."""
        for gloss in sense["SenseGloss"]:
            if gloss["lang"] == "eng":
                return cls.parse(gloss["text"])

        return JmneGloss()

    @classmethod
    def parse(cls, gloss: str) -> JmneGloss:
        """Parse English gloss from a string."""
        obj = JmneGloss(source_string=gloss)

        if m := re.search(cls.DATE_SPAN_PAT, gloss):
            birth, death = None, None

            birth_str, death_str = m.groups()
            if birth_str and birth_str != "?":
                birth = int(birth_str)
            if death_str:
                death = int(death_str)

            obj.lifetime = Lifetime(birth, death)

        if m := re.search(r"^(\w+ (?:[Nn]o )?\w+)", gloss):
            obj.name = m[1]

        return obj
