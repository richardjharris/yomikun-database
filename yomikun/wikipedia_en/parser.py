"""
Parser for English-language Wikipedia articles.

TODO: {{nihongo}} is used for non-name stuff too. Examples include
  {{Nihongo|Tokyo Tower|東京タワー|Tōkyō tawā}}

TODO: second argument is optional.
TODO: honmyo is listed as 'born ' in the extra content.

TODO: a few do not use {{nihongo}} but they seem very rare!

It's possible the template birth/death can be used to filter these
out.

TODO: Natsume Soseki
{{nihongo|'''Natsume Sōseki'''|夏目 漱石|extra=9 February 1867&nbsp;– 9 December 1916}}, born '''{{nihongo|Natsume Kin'nosuke|夏目 金之助}}''', was a [[Japanese people|Japanese]] novelist. He is best known around the world for his novels ''[[Kokoro]]'', ''[[Botchan]]'', ''[[I Am a Cat]]'', ''[[Kusamakura (novel)|Kusamakura]]'' and his unfinished work ''[[Light and Darkness (novel)|Light and Darkness]]''. He was also a scholar of [[British literature]] and writer of [[haiku]], ''[[Kanshi (poetry)|kanshi]]'', and [[fairy tale]]s. From 1984 until 2004, his portrait appeared on the front of the Japanese [[Banknotes of the Japanese yen|1000 yen note]].

 ^ no extra argument here! oops... what a pain...
"""


from __future__ import annotations
import logging
import enum
import sys
from yomikun.wikipedia_ja.ignore import should_ignore_name

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import NameData, NameAuthenticity, Lifetime
from yomikun.utils.patterns import name_pat, reading_pat, name_paren_start
from yomikun.utils.split import split_kanji_name
from yomikun.utils.romaji import romaji_to_hiragana_messy


class Gender(enum.Enum):
    unknown = 1
    male = 2
    female = 3


CATEGORY_PAT = r'\[\[[cC]ategory:(.*?)\]\]'


def get_categories(content: str) -> list[str]:
    """
    Returns an array of category names extracted from the MediaWiki page content.
    """
    return regex.findall(CATEGORY_PAT, content)


def notes_from_categories(categories: list[str]) -> str | None:
    """
    Returns a short summary of this person (occupation etc.) based on
    the article categories
    """
    for category in categories:
        if category == 'Manga artists':
            return 'manga artist'
        if m := regex.match(r'^Japanese (?:male |female )?(writer|philosopher|artist|singer)s', category):
            return m[1].capitalize()

    return


ROMAJI = r"[A-Za-zŌōā']"
ROMAJI_NAME = ROMAJI + r'+\s+' + ROMAJI + '+'

NIHONGO_TEMPLATE_PAT = r'\{\{' + \
    fr"[Nn]ihongo\|'''{ROMAJI_NAME}'''\|({name_pat})\|({ROMAJI_NAME})(?:\|(.*?))?" + \
    r'\}\}(.{1,5000})'


def parse_wikipedia_article(title: str, content: str, add_source: bool = True) -> NameData | None:
    """
    Parse en.wikipedia article for names/readings and return the primary one.
    """
    if m := regex.search(NIHONGO_TEMPLATE_PAT, content, regex.S):
        kanji, romaji, template_extra, rest_of_line = m.groups()

        # Clean doesn't remove '' ... '' (??)
        romaji = regex.sub(r"^''(.*?)''$", r"\1", romaji)

        kana = romaji_to_hiragana_messy(clean(romaji), kanji)

        kanji = split_kanji_name(kanji, kana)

        namedata = NameData(kaki=kanji, yomi=kana, tags=['xx-romaji'])
        gender = Gender.unknown

        if regex.search(r'\bfictional\b', rest_of_line):
            namedata.authenticity = NameAuthenticity.FICTIONAL
        elif regex.search(r"\b[Bb]orn\s*(?:''')?" + NIHONGO_TEMPLATE_PAT, content, regex.S, pos=m.end()):
            namedata.authenticity = NameAuthenticity.PSEUDO
            # TODO
        elif regex.search(r"\b[Bb]orn\s+'''", content):
            # e.g. Knock Yokoyama: Born '''Isamu Yamada''' (山田勇 ''Yamada Isamu'')
            # Born\s*\p{Han} won't work due to FP: "born on July 14, 1986, in [[Uozu, Toyama]].<ref>{{cite web|url=https://www.shogi.or.jp/player/pro/267.html|script-title=ja:棋士データベース(...)"
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
            m = regex.search(r'(?:^|\b)(he|his|she|her)\b',
                             rest_of_line, regex.I)
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

        # Figure out what kind of person this is
        if not namedata.notes:
            cleaned_first_sentence = clean(rest_of_line)
            if m := regex.match(r'(?:.*?[,\)])?\s*(?:is|was) (?:the|a|an) (.+?)[.]', cleaned_first_sentence):
                desc = m[1]
                namedata.notes = desc[0].upper() + desc[1:]
            elif m := regex.match(r'^\{\{Infobox (.*?)', content):
                namedata.notes = m[1]
            elif notes := notes_from_categories(categories):
                namedata.notes = notes

        # 'Japanese' is usually implied
        namedata.notes = regex.sub(
            r'^Japanese (\w)(.*)$', lambda m: m[1].upper() + m[2], namedata.notes)
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
        logging.info(
            f"[{title}] Name '{namedata.kaki}' could not be split, skipping")
        return
    elif should_ignore_name(namedata.kaki):
        if namedata.authenticity == NameAuthenticity.REAL:
            logging.info(
                f"[{title}] Name '{namedata.kaki}' matched ignore rules, skipping")
            return
        else:
            logging.info(
                f"[{title}] Name '{namedata.kaki}' matched ignore rules but character is not real - allowing")
            pass
    elif not namedata.lifetime:
        if namedata.authenticity == NameAuthenticity.REAL:
            logging.info(f"[{title}] No birth / death year found, skipping")
            return
        else:
            logging.info(
                f"[{title}] No birth / death year found, but character is not real - allowing")
            pass

    namedata.add_tag('person')
    namedata.clean_and_validate()

    if add_source:
        namedata.source = f'wikipedia_en:{title}'

    return namedata


def test_basic():
    content = """
{{nihongo|'''Akifumi Endō'''|遠藤 章史|Endō Akifumi|born December 10, 1964}} is a Japanese [[Seiyū|voice actor]] who is affiliated with [[Troubadour Musique Office]].
[[Category:Japanese male voice actors]]
[[Category:1964 births]]
""".strip()
    assert parse_wikipedia_article('Akifumi Endo', content) == NameData(
        kaki='遠藤 章史',
        yomi='えんどう あきふみ',
        lifetime=Lifetime(1964),
        tags=['xx-romaji', 'masc', 'person'],
        source='wikipedia_en:Akifumi Endo',
        notes='Voice actor who is affiliated with Troubadour Musique Office',
    ), 'extracts gender from category'


def test_fail():
    assert parse_wikipedia_article('Sausages', 'Sausages') is None


def test_gender_from_text():
    content = """
{{Expand Japanese|date=December 2017}}
{{Nihongo|'''Akihiro Murata'''|村田 顕弘|Murata Akihiro|born July 14, 1986}} is a Japanese [[professional shogi player]] ranked 6-[[Dan (rank)#Modern usage in shogi|dan]].

==Early life==
Murata was born on July 14, 1986, in [[Uozu, Toyama]].<ref>{{cite web|url=https://www.shogi.or.jp/player/pro/267.html|script-title=ja:棋士データベース: 村田顕弘|title=Kishi Dētabēsu: Murata Akihiro|language=Japanese|trans-title=Professional Shogi Player Database: Akihiro Murata|publisher=[[Japan Shogi Association]]|access-date=February 28, 2019}}</ref>  He learned how to play shogi when he was about five years old from his father.<ref name="New 4ds">{{cite web|url=https://www.shogi.or.jp/news/2007/09/post_126.html|script-title=ja:村田顕弘･及川拓馬 新四段誕生のお知らせ|title=Murata Akihiro･Oikawa Takuma Shinyondan Tanjō no Oshirase|language=ja|trans-title=New 4-dan announced: Akihiro Murata and Takuma Oikawa|date=September 17, 2017|publisher=Japan Shogi Association|access-date=February 28, 2019}}</ref> In 1998, Murata took the entrance exam for the [[Japan Shogi Association]]'s [[Professional shogi player#Apprenticeship|apprentice school]], but failed;<ref name="2016databook">{{cite book|url=https://books.google.com/books?id=bWVDCwAAQBAJ&pg=PA56|script-title=ja:現役プロ棋士データブック2016 [下] た-わ行|title=Geneki Purō Kishi DētaBukku 2016 [Ge] Ta-Wa Gyō|language=Japanese|trans-title=2016 Active Shogi Professional Databook [Last volume] Letter "Ta" to letter "Wa"|year=2015|page=56|publisher=MyNabi Publishing/Japan Shogi Association|via=[[Google Books]]|asin=B019SSNKVA|access-date=February 28, 2019}}</ref> he tried again the following year and was accepted at the rank of 6-[[Dan (rank)#Modern usage in shogi|kyū]] under the guidance of shogi professional {{ill|Shōdō Nakada|ja|中田章道}}.<ref name="2016databook" /><ref name="2014yearbook">{{cite magazine|author=<!--Staff writer(s); no by-line-->|url=https://books.google.com/books?id=7UEcBAAAQBAJ&pg=PA576|script-title=ja:平成26年版 将棋年鑑 2014|title=Heisei Nijūrokunenban Shōgi Nenkan Nisenjūyonnen|language=ja|trans-title=Shogi Yearbook: Heisei 26 (2014) edition|page=576|year=2014|publisher=MyNabi Publishing/Japan Shogi Association|via=Google Books|isbn=978-4-8399-5175-7|access-date=February 28, 2019}}</ref>

[[Category:1986 births]]
""".strip()
    assert parse_wikipedia_article('Akihiro Murata', content) == NameData(
        kaki='村田 顕弘',
        yomi='むらた あきひろ',
        lifetime=Lifetime(1986),
        tags=['xx-romaji', 'masc', 'person'],
        source='wikipedia_en:Akihiro Murata',
        notes='Professional shogi player ranked 6-dan',
    ), 'extracts gender from text'


def test_nya_romaji():
    content = """
{{Nihongo|'''Junya Kato'''|加藤 潤也|Katō Jun'ya|born December 30, 1994}} is a [[Japanese people|Japanese]] [[Association football|football]] player.<ref>{{J.League player|23134}}</ref> He plays for [[Gainare Tottori]].
[[Category:1994 births]]
[[Category:Association football forwards]]
""".strip()
    assert parse_wikipedia_article('Junya Kato', content) == NameData(
        kaki='加藤 潤也',
        yomi='かとう じゅんや',
        lifetime=Lifetime(1994),
        tags=['xx-romaji', 'masc', 'person'],
        source='wikipedia_en:Junya Kato',
        notes='Football player',
    ), 'should not convert to じゅにゃ'


def test_knock():
    content = """
{{nihongo|'''Knock Yokoyama'''|横山 ノック|Yokoyama Nokku|January 30, 1932 – May 3, 2007}} was a [[Japan]]ese [[politician]] and [[comedian]].

Born '''Isamu Yamada''' (山田勇 ''Yamada Isamu'') in [[Kobe]], he adopted his current stage name while directing the ''Manga Trio'' [[manzai]] troupe from 1959 to 1968. Following his comedy years, he went into the construction industry and served as a director at several major construction firms in the [[Kansai]] region.

He became governor of [[Osaka prefecture]] in 1995, running as an independent and joining the [[Liberal Democratic Party (Japan)|Liberal Democratic Party]] (LDP) after his election. He enjoyed great popularity as governor, mostly due to his existing fame as a comedian.

In 2000, a 21-year-old campaign volunteer accused Yokoyama of [[sexual harassment]], claiming that the governor groped her for 30 minutes in the back of a campaign truck. Yokoyama denied the charges, but the Osaka District Court found him liable for ¥11 million in damages, following a highly publicized trial in which the plaintiff testified from behind an opaque screen to avoid revealing her identity. Following the judgment, Yokoyama resigned: he was replaced by a female LDP bureaucrat, [[Fusae Ohta]].
[[Category:1932 births]]
[[Category:2007 deaths]]
""".strip()
    result = parse_wikipedia_article('Knock Yokoyama', content)
    # We don't expect Yamada Isamu to be extracted, but we do want to mark it as pseudo at least
    assert result == NameData(
        kaki='横山 ノック',
        yomi='よこやま のっく',
        lifetime=Lifetime(1932, 2007),
        authenticity=NameAuthenticity.PSEUDO,
        tags=['xx-romaji', 'masc', 'person'],
        source='wikipedia_en:Knock Yokoyama',
        notes='Politician and comedian',
    )


def test_allow_fictional_character_with_no_lifetime():
    content = """
{{nihongo|'''Mai Shiranui'''|不知火 舞|Shiranui Mai|lead=yes}} (alternatively written しらぬい まい) is a [[fictional character]] in the ''[[Fatal Fury]]'' and ''[[The King of Fighters]]'' series of [[fighting game]]s by [[SNK]]. She has also appeared in other media of these franchises and in a number of other games since her debut in 1992's ''[[Fatal Fury 2]]'' as the first female character in an SNK fighting game. She also appears in the games' various manga and anime adaptations and plays a leading role in the [[The King of Fighters (film)|live-action film]].    
""".strip()
    assert parse_wikipedia_article('foo', content) == NameData.person(
        kaki='不知火 舞',
        yomi='しらぬい まい',
        authenticity=NameAuthenticity.FICTIONAL,
        source='wikipedia_en:foo',
        tags=['xx-romaji', 'fem'],
        notes='Fictional character in the Fatal Fury and The King of Fighters series of fighting games by SNK'
    )
