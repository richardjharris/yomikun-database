from __future__ import annotations

import re
from operator import itemgetter

import jcconv3
import regex

from yomikun.models import Gender, NameData, NamePosition
from yomikun.parsers.jmnedict.jmnegloss import JmneGloss
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy
from yomikun.utils.split import split_kanji_name

NAME_TYPES_WE_WANT = {"fem", "given", "person", "masc", "surname", "unclass"}


def parse_jmnedict_entry(data: dict) -> list[NameData]:
    records_out = []

    for sense in data["senses"]:
        name_types = set(sense["name_type"]).intersection(NAME_TYPES_WE_WANT)
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

                # Handle katakana yomi such as ウメこ for ウメ子
                if regex.search(r"\p{Katakana}", kana):
                    kana = jcconv3.kata2hira(kana)

                base_data = NameData(kanji, kana, source="jmnedict", is_dict=True)
                if gloss.lifetime:
                    base_data.lifetime = gloss.lifetime

                # Generate NameData for each name type - some JMnedict entries can have
                # multiple name types (e.g. ['surname', 'given'])
                if "person" in name_types:
                    namedata = base_data.clone()
                    namedata.is_dict = False
                    namedata.position = NamePosition.person
                    if "fem" in name_types:
                        namedata.gender = Gender.female
                    elif "masc" in name_types:
                        namedata.gender = Gender.male

                    # Normalise whitespace
                    namedata.clean()
                    records_out.append(namedata)
                else:
                    if "unclass" in name_types:
                        namedata = base_data.clone()
                        namedata.position = NamePosition.unknown
                        records_out.append(namedata)

                    if "surname" in name_types:
                        namedata = base_data.clone()
                        namedata.position = NamePosition.sei
                        records_out.append(namedata)

                    if name_types & {"masc", "fem", "given"}:
                        namedata = base_data.clone()
                        namedata.position = NamePosition.mei
                        # ignore gender tag, as it is untrustworthy
                        records_out.append(namedata)

    return records_out
