from __future__ import annotations
from operator import itemgetter
import re
from dataclasses import dataclass, field
from yomikun.utils.romaji import romaji_to_hiragana

import romkan

from yomikun.models import Lifetime
from yomikun.utils.split import split_kanji_name


name_types_we_want = {'fem', 'given',
                      'person', 'masc', 'surname', 'unclass'}


@dataclass
class JmneGloss:
    # Match a YYYY.MM.DD date and capture the year
    DATE_PAT = r'(\d{3,4})(?:\.\d\d?(?:\.\d\d?)?)?'
    # Match (date-date) or (date-)
    # some are like 'Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)' so
    # we also match on a preceding comma.
    DATE_SPAN_PAT = re.compile(fr'[\(, ]{DATE_PAT}-(?:{DATE_PAT})?\)$')
    NAME_PAT = re.compile(r'^(\w+ \w+)')

    name: str | None = None
    lifetime: Lifetime = field(default_factory=Lifetime)
    source_string: str | None = None

    @classmethod
    def parse_from_sense(cls, sense) -> JmneGloss:
        """Parse English gloss from a Sense object"""
        for gloss in sense['SenseGloss']:
            if gloss['lang'] == 'eng':
                return cls.parse(gloss['text'])

        return JmneGloss()

    @classmethod
    def parse(cls, gloss: str) -> JmneGloss:
        obj = JmneGloss(source_string=gloss)

        if m := re.search(cls.DATE_SPAN_PAT, gloss):
            birth, death = m.groups()
            obj.lifetime = Lifetime(int(birth), int(
                death) if death else None)

        if m := re.match(r'^(\w+ \w+)', gloss):
            obj.name = m[1]

        return obj


def parse(data: dict, with_orig=True) -> list[dict]:
    records_out = []

    for sense in data['senses']:
        name_types = set(sense['name_types']).intersection(
            name_types_we_want)
        if not name_types:
            continue

        if 'person' in name_types:
            # Extract lifetime if available
            gloss = JmneGloss.parse_from_sense(sense)
        else:
            gloss = JmneGloss()

        for kanji in map(itemgetter('text'), data['kanji']):
            for kana in map(itemgetter('text'), data['kana']):
                if gloss.name:
                    # Convert name to hiragana and use it to split the name
                    # TODO other 4 vowels
                    split_kana = romaji_to_hiragana(gloss.name)
                    split_kanji = split_kanji_name(kanji, split_kana)
                    if kanji != split_kanji:
                        kanji, kana = split_kanji, split_kana

                output = {
                    'kaki': kanji,
                    'yomi': kana,
                    'tags': list(name_types),
                }
                if with_orig:
                    output['orig'] = gloss.source_string
                if gloss.lifetime:
                    output['lifetime'] = gloss.lifetime.to_dict()

                records_out.append(output)

    return records_out


def test_basic():
    data = {'idseq': 5000254, 'kanji': [{'text': 'あき竹城'}], 'kana': [{'text': 'あきたけじょう', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [{'lang': 'eng', 'text': 'Aki Takejou (1947.4-)'}], 'name_types': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': 'あき 竹城', 'yomi': 'あき たけじょう', 'tags': ['person'],
         'lifetime': {'birth_year': 1947, 'death_year': None}},
    ]


def test_sumo():
    data = {'idseq': 2831743, 'kanji': [{'text': '蒼国来栄吉'}], 'kana': [{'text': 'そうこくらいえいきち', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [
            {'lang': 'eng',
                'text': 'Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)'},
            {'lang': 'eng', 'text': 'Engketübsin'}],
         'name_types': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': '蒼国来 栄吉', 'yomi': 'そうこくらい えいきち', 'tags': ['person'],
         'lifetime': {'birth_year': 1984, 'death_year': None}},
    ]
