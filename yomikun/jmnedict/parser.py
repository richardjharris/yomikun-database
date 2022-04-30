from __future__ import annotations
from operator import itemgetter
import re
from dataclasses import dataclass, field
from typing import cast
from yomikun.models.namedata import NameData
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy

from yomikun.models import Lifetime
from yomikun.utils.split import split_kanji_name


name_types_we_want = {"fem", "given", "person", "masc", "surname", "unclass"}


@dataclass
class JmneGloss:
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
        """Parse English gloss from a Sense object"""
        for gloss in sense["SenseGloss"]:
            if gloss["lang"] == "eng":
                return cls.parse(gloss["text"])

        return JmneGloss()

    @classmethod
    def parse(cls, gloss: str) -> JmneGloss:
        obj = JmneGloss(source_string=gloss)

        if m := re.search(cls.DATE_SPAN_PAT, gloss):
            birth, death = None, None

            birth_str, death_str = m.groups()
            if birth_str and birth_str != "?":
                birth = int(birth_str)
            if death_str:
                death = int(death_str)

            obj.lifetime = Lifetime(birth, death)

        if m := re.match(r"^(\w+ (?:[Nn]o )?\w+)", gloss):
            obj.name = m[1]

        return obj


def parse(data: dict) -> list[NameData]:
    records_out = []

    for sense in data["senses"]:
        name_types = set(sense["name_type"]).intersection(name_types_we_want)
        if not name_types:
            continue

        if "person" in name_types:
            # Extract lifetime if available
            gloss = JmneGloss.parse_from_sense(sense)
        else:
            gloss = JmneGloss()

        for kanji in map(itemgetter("text"), data["kanji"]):
            for kana in map(itemgetter("text"), data["kana"]):
                if gloss.name:
                    # Convert name to hiragana and use it to split the name
                    # TODO: this is not 100% accurate, some names are not written in standard
                    #       Romaji. In these cases we just don't split anything.
                    # TODO: ... would be unwise to use these unsplit entries in the dictionary!!
                    #       Luckily they are tagged as 'person'. Double-check though...
                    split_kana = romaji_to_hiragana_messy(gloss.name)
                    split_kanji = kanji

                    if " の " in split_kana:
                        # Middle name of 'の', used in some older names.
                        # It will either be missing from the kanji, or before the firstname
                        split_kana = re.sub(" の ", " ", split_kana)
                        split_kanji = re.sub("の", " ", split_kanji)

                    split_kanji = split_kanji_name(split_kanji, split_kana)

                    if kanji != split_kanji:
                        kanji, kana = split_kanji, split_kana

                tags = cast(set[str], name_types.copy())

                # Indicates that this is a dictionary entry, not a real-world name
                # sighting
                if "person" not in tags:
                    tags.add("dict")

                    # Map fem/masc to given, as gender information is untrustworthy
                    if tags.intersection({"masc", "fem"}):
                        tags -= {"masc", "fem"}
                        tags.add("given")

                namedata = NameData(kanji, kana, tags=tags, source="jmnedict")

                if gloss.lifetime:
                    namedata.lifetime = gloss.lifetime

                records_out.append(namedata)

    return records_out
