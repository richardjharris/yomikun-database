"""
Parser for English-language Wikipedia articles.
"""


import logging

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import Gender, NameAuthenticity, NameData
from yomikun.parsers.wikipedia_ja.ignore import should_ignore_name
from yomikun.researchmap import ResearchMapRecord

# XXX: importing private function
from yomikun.researchmap.parser import _parse_researchmap_inner
from yomikun.utils.patterns import name_pat
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy
from yomikun.utils.split import split_kanji_name

CATEGORY_PAT = r'\[\[[cC]ategory:(.*?)\]\]'


def get_categories(content: str) -> list[str]:
    """
    Returns an array of category names extracted from the MediaWiki page content.
    """
    return regex.findall(CATEGORY_PAT, content)


PROFESSIONS = [
    'writer',
    'philosopher',
    'artist',
    'singer',
    'baseball player',
    'professional wrestler',
    'television actor',
    'voice actor',
    'footballer',
    'lawyer',
]
PROF_REGEX = regex.compile(
    r"^Japanese (?:male |female )?(\L<professions>)", professions=PROFESSIONS
)


def notes_from_categories(categories: list[str]) -> str | None:
    """
    Returns a short summary of this person (occupation etc.) based on
    the article categories
    """
    for category in categories:
        if category == 'Manga artists':
            return 'Manga artist'
        if m := regex.match(PROF_REGEX, category):
            return m[1].capitalize()

    return


ROMAJI = r"[A-Za-zŌōā']"
ROMAJI_NAME = ROMAJI + r'+\s+' + ROMAJI + '+'

# TODO what if the 3rd arg is missing? 1st arg is usually romaji also, just in reverse order
NIHONGO_TEMPLATE_PAT = (
    r'\{\{'
    + fr"[Nn]ihongo\|'''{ROMAJI_NAME}'''\|({name_pat})\|({ROMAJI_NAME})(?:\|(.*?))?"
    + r'\}\}(.{1,5000})'
)


def parse_wikipedia_article(
    title: str, content: str, add_source: bool = True
) -> NameData | None:
    """
    Parse en.wikipedia article for names/readings and return the primary one.
    """
    if m := regex.search(NIHONGO_TEMPLATE_PAT, content, regex.S):
        kanji, romaji, _template_extra, rest_of_line = m.groups()

        # Clean doesn't remove '' ... '' (??)
        romaji = regex.sub(r"^''(.*?)''$", r"\1", romaji)

        # HACK: Use researchmap code.
        # TODO: replace with nicer abstraction.
        namedata = None
        try:
            record = ResearchMapRecord(romaji, kanji, '')
            namedata = _parse_researchmap_inner(record, swap_names=True)
        except NotImplementedError:
            pass

        if not namedata:
            # Fall back to messy code
            kana = romaji_to_hiragana_messy(clean(romaji), kanji)
            kanji = split_kanji_name(kanji, kana)
            namedata = NameData(kanji, kana).add_tag('xx-romaji')

        gender = Gender.unknown

        if regex.search(r'\bfictional\b', rest_of_line):
            namedata.authenticity = NameAuthenticity.FICTIONAL
        elif regex.search(
            r"\b[Bb]orn\s*(?:''')?" + NIHONGO_TEMPLATE_PAT,
            content,
            regex.S,
            pos=m.end(),
        ):
            namedata.authenticity = NameAuthenticity.PSEUDO
            # TODO
        elif regex.search(r"\b[Bb]orn\s+'''", content):
            # e.g. Knock Yokoyama: Born '''Isamu Yamada''' (山田勇 ''Yamada Isamu'')
            # Born\s*\p{Han} won't work due to FP: "born on July 14, 1986, in [[Uozu, Toyama]].\
            # <ref>{{cite web|url=https://www.shogi.or.jp/player/pro/267.html|script-title=ja:棋士データベース(...)" # noqa
            namedata.authenticity = NameAuthenticity.PSEUDO

        # Extract data from categories
        categories = get_categories(content)
        for category in categories:
            if m := regex.search(r'^(\d{3,4}) births$', category):
                namedata.lifetime.birth_year = int(m[1])
            elif m := regex.search(r'^(\d{3,4}) deaths$', category):
                namedata.lifetime.death_year = int(m[1])
            elif regex.search(r'(\b|^)male\b', category, regex.I):
                gender = Gender.male
            elif regex.search(r'(\b|^)(female|woman)\b', category, regex.I):
                gender = Gender.female

        if gender == Gender.unknown:
            m = regex.search(r'(?:^|\b)(he|his|she|her)\b', rest_of_line, regex.I)
            if m:
                matched: str = m[1].lower()
                if matched in ('he', 'his'):
                    gender = Gender.male
                if matched in ('she', 'her'):
                    gender = Gender.female

        if gender == Gender.male:
            namedata.add_tag('masc')
        elif gender == Gender.female:
            namedata.add_tag('fem')

        # Find out what kind of person this is
        # Prefer a simple description from the categories
        if notes := notes_from_categories(categories):
            namedata.notes = notes
        else:
            # Remove <ref>, as clean() will keep the tag contents by default
            rest_of_line = regex.sub(r'<ref>.*?</ref>', '', rest_of_line)

            cleaned_first_sentence = clean(rest_of_line)

            if m := regex.match(
                r'(?:.*?[,\)])?\s*(?:is|was) (?:the|a|an) (.+?)[.]',
                cleaned_first_sentence,
            ):
                desc = m[1]
                namedata.notes = desc[0].upper() + desc[1:]
            elif m := regex.match(r'^\{\{Infobox (.*?)', content):
                namedata.notes = m[1]

        # 'Japanese' is usually implied
        namedata.notes = regex.sub(
            r'^Japanese (\w)(.*)$', lambda m: m[1].upper() + m[2], namedata.notes
        )

        # Remove italic
        namedata.notes = regex.sub(r"'{2,}", '', namedata.notes)
    else:
        # Return an empty record
        logging.info(f"[{title}] No nihongo template found, skipping")
        return

    if not namedata.has_name():
        logging.info(f"[{title}] No name found, skipping")
        return

    # Exclude probable false positives.
    # This includes cases where we could not split the name, obviously invalid
    # names, and (for the English wikipedia only) cases where we have no birth
    # or death year. Examples:
    #  - 拡張新字体 (from 'Extended shinjitai' page)
    #  - 亜馬尻 菊の助 (name from the 'Characters' section of a series page)
    #  - 艦隊これくしょん
    if len(namedata.kaki.split()) == 1:
        logging.info(f"[{title}] Name '{namedata.kaki}' could not be split, skipping")
        return
    elif should_ignore_name(namedata.kaki):
        if namedata.authenticity == NameAuthenticity.REAL:
            logging.info(
                f"[{title}] Name '{namedata.kaki}' matched ignore rules, skipping"
            )
            return
        else:
            logging.info(
                f"[{title}] Name '{namedata.kaki}' matched ignore rules but character "
                "is not real - allowing"
            )
            pass
    elif not namedata.lifetime:
        if namedata.authenticity == NameAuthenticity.REAL:
            logging.info(f"[{title}] No birth / death year found, skipping")
            return
        else:
            logging.info(
                f"[{title}] No birth / death year found, but character is not real - allowing"
            )
            pass

    namedata.add_tag('person')
    namedata.clean_and_validate()

    if add_source:
        namedata.source = f'wikipedia_en:{title}'

    return namedata
