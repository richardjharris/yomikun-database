from __future__ import annotations
from operator import itemgetter
import re
from dataclasses import dataclass, field
from yomikun.utils.romaji import romaji_to_hiragana_messy

from yomikun.models import Lifetime
from yomikun.utils.split import split_kanji_name


name_types_we_want = {'fem', 'given',
                      'person', 'masc', 'surname', 'unclass'}


@dataclass
class JmneGloss:
    # Match a YYYY.MM.DD date and capture the year
    DATE_PAT = r'(\d{3,4})(?:\.\d\d?(?:\.\d\d?)?|[?]|)'
    # Match (date-date) or (date-)
    # some are like 'Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)' so
    # we also match on a preceding comma.
    DATE_SPAN_PAT = re.compile(fr'[\(, ]{DATE_PAT}-(?:{DATE_PAT})?\)')
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
            birth, death = None, None

            birth_str, death_str = m.groups()
            if birth_str and birth_str != '?':
                birth = int(birth_str)
            if death_str:
                death = int(death_str)

            obj.lifetime = Lifetime(birth, death)

        if m := re.match(r'^(\w+ (?:[Nn]o )?\w+)', gloss):
            obj.name = m[1]

        return obj


def parse(data: dict, with_orig=True) -> list[dict]:
    records_out = []

    for sense in data['senses']:
        name_types = set(sense['name_type']).intersection(
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
                    # TODO: this is not 100% accurate, some names are not written in standard
                    #       Romaji. In these cases we just don't split anything.
                    # TODO: ... would be unwise to use these unsplit entries in the dictionary!!
                    #       Luckily they are tagged as 'person'. Double-check though...
                    split_kana = romaji_to_hiragana_messy(gloss.name)
                    split_kanji = kanji

                    if ' の ' in split_kana:
                        # Middle name of 'の', used in some older names.
                        # It will either be missing from the kanji, or before the firstname
                        split_kana = re.sub(' の ', ' ', split_kana)
                        split_kanji = re.sub('の', ' ', split_kanji)

                    split_kanji = split_kanji_name(split_kanji, split_kana)

                    if kanji != split_kanji:
                        kanji, kana = split_kanji, split_kana

                output = {
                    'kaki': kanji,
                    'yomi': kana,
                    'tags': list(name_types),
                    'source': 'jmnedict',
                }
                if with_orig:
                    output['orig'] = gloss.source_string
                if gloss.lifetime:
                    output['lifetime'] = gloss.lifetime.to_dict()

                records_out.append(output)

    return records_out


def test_basic():
    data = {'idseq': 5000254, 'kanji': [{'text': 'あき竹城'}], 'kana': [{'text': 'あきたけじょう', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [{'lang': 'eng', 'text': 'Aki Takejou (1947.4-)'}], 'name_type': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': 'あき 竹城', 'yomi': 'あき たけじょう', 'tags': ['person'],
         'lifetime': {'birth_year': 1947, 'death_year': None}, 'source': 'jmnedict'},
    ]


def test_sumo():
    data = {'idseq': 2831743, 'kanji': [{'text': '蒼国来栄吉'}], 'kana': [{'text': 'そうこくらいえいきち', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [
            {'lang': 'eng',
                'text': 'Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)'},
            {'lang': 'eng', 'text': 'Engketübsin'}],
         'name_type': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': '蒼国来 栄吉', 'yomi': 'そうこくらい えいきち', 'tags': ['person'],
         'lifetime': {'birth_year': 1984, 'death_year': None}, 'source': 'jmnedict'},
    ]


def test_taira():
    data = {'idseq': 5629450, 'kanji': [{'text': '平知盛'}], 'kana': [{'text': 'たいらのとももり', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [{'lang': 'eng', 'text': 'Taira No Tomomori (1151-1185.4.25)'}], 'name_type': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': '平 知盛', 'yomi': 'たいら とももり', 'tags': ['person'],
         'lifetime': {'birth_year': 1151, 'death_year': 1185}, 'source': 'jmnedict'},
    ]


def test_oumi():
    data = {'idseq': 5228414, 'kanji': [{'text': '近江の君'}], 'kana': [{'text': 'おうみのきみ', 'nokanji': 0}], 'senses': [
        {'SenseGloss': [{'lang': 'eng', 'text': 'Oumi no Kimi (Genji Monogatari)'}], 'name_type': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': '近江 君', 'yomi': 'おうみ きみ', 'tags': [
            'person'], 'source': 'jmnedict'},
    ]


def test_long_u():
    data = {'idseq': 5459611, 'kanji': [{'text': '千の利休'}], 'kana': [{'text': 'せんのりきゅう', 'nokanji': 0}], 'senses': [{'SenseGloss': [
        {'lang': 'eng', 'text': 'Sen no Rikyū (1522-1591) (founder of the Sen School of tea ceremony)'}], 'name_type': ['person']}]}
    result = parse(data, with_orig=False)
    assert result == [
        {'kaki': '千 利休', 'yomi': 'せん りきゅう', 'tags': ['person'],
         'lifetime': {'birth_year': 1522, 'death_year': 1591}, 'source': 'jmnedict'},
    ]
