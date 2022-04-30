from __future__ import annotations
import copy
from dataclasses import dataclass

from yomikun.models import NameData, NameAuthenticity
from yomikun.loader.models import Gender, NamePosition


@dataclass(frozen=True)
class NamePart:
    kaki: str
    yomi: str
    position: NamePosition


class Aggregator:
    @staticmethod
    def copy_data_to_subreadings(data: NameData):
        """
        Copy information in the main NameData reading to its subreadings
        if applicable.
        """
        for subreading in data.subreadings:
            # Copy over the lifetime / gender / source to the real actor
            if (
                data.authenticity == NameAuthenticity.PSEUDO
                and subreading.authenticity == NameAuthenticity.REAL
            ):
                if data.lifetime and not subreading.lifetime:
                    subreading.lifetime = copy.copy(data.lifetime)
                if data.source and not subreading.source:
                    subreading.source = data.source
                if data.tags and not subreading.tags:
                    subreading.tags = data.tags

    @staticmethod
    def extract_name_parts(data: NameData) -> list[tuple[NamePart, Gender | None]]:
        parts = []
        if data.is_person():
            # Sometimes is tagged [person, fem] to indicate the person's gender.
            gender = Aggregator.gender_from_tags(data.tags)
            kakis = data.kaki.split()
            yomis = data.yomi.split()
            if len(kakis) == 2 and len(yomis) == 2:
                sei = NamePart(kaki=kakis[0], yomi=yomis[0], position=NamePosition.sei)
                mei = NamePart(kaki=kakis[1], yomi=yomis[1], position=NamePosition.mei)
                parts += [(sei, gender), (mei, gender)]
            else:
                # Can't reliably assign positions to names
                part = NamePart(
                    kaki=data.kaki, yomi=data.yomi, position=NamePosition.unknown
                )
                parts.append((part, gender))
        elif 'unclass' in data.tags:
            for tag in ('person', 'surname', 'given', 'fem', 'masc'):
                assert not data.has_tag(tag)

            part = NamePart(
                kaki=data.kaki, yomi=data.yomi, position=NamePosition.unknown
            )
            parts.append((part, None))
        else:
            # Names may be a combination of masc,fem,given,surname
            if 'surname' in data.tags:
                sei = NamePart(
                    kaki=data.kaki, yomi=data.yomi, position=NamePosition.sei
                )
                parts.append((sei, None))
            elif set(data.tags).intersection({'masc', 'fem', 'given'}):
                gender = Aggregator.gender_from_tags(data.tags)
                mei = NamePart(
                    kaki=data.kaki, yomi=data.yomi, position=NamePosition.mei
                )
                parts.append((mei, gender))

        return parts

    @staticmethod
    def gender_from_tags(tags) -> Gender:
        if 'masc' in tags and 'fem' in tags:
            return Gender.neutral
        elif 'masc' in tags:
            return Gender.male
        elif 'fem' in tags:
            return Gender.female
        else:
            return Gender.unknown
