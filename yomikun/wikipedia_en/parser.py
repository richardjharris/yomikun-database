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

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import NameData, NameAuthenticity, Lifetime
from yomikun.utils.patterns import name_pat, reading_pat, name_paren_start
from yomikun.utils.split import split_kanji_name
from yomikun.utils.romaji import romaji_to_hiragana

ROMAJI = r"[A-Za-zŌōā']"
ROMAJI_NAME = ROMAJI + r'+\s+' + ROMAJI + '+'

NIHONGO_TEMPLATE_PAT = r'\{\{' + \
    fr"[Nn]ihongo\|'''{ROMAJI_NAME}'''\|({name_pat})\|({ROMAJI_NAME})\|(.*?)" + \
    r'\}\}(.{1,5000})'

CATEGORY_PAT = r'\[\[Category:(.*?)\]\]'


class Gender(enum.Enum):
    unknown = 1
    male = 2
    female = 3


def get_categories(content: str) -> list[str]:
    """
    Returns an array of category names extracted from the MediaWiki page content.
    """
    return regex.findall(CATEGORY_PAT, content)


def parse_wikipedia_article(title: str, content: str, add_source: bool = True) -> NameData:
    """
    Parse en.wikipedia article for names/readings and return the primary one.
    """
    if m := regex.search(NIHONGO_TEMPLATE_PAT, content, regex.S):
        kanji, romaji, template_extra, rest_of_line = m.groups()
        kana = romaji_to_hiragana(romaji)

        kanji = split_kanji_name(kanji, kana)

        namedata = NameData(kaki=kanji, yomi=kana)
        gender = Gender.unknown

        if regex.search(r'\bfictional\b', rest_of_line):
            namedata.authenticity = NameAuthenticity.FICTIONAL
        elif m := regex.search(r"born\s*(?:''')?" + NIHONGO_TEMPLATE_PAT, content, regex.S, pos=m.end()):
            namedata.authenticity = NameAuthenticity.PSEUDO
            # TODO
            pass

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
    else:
        # Return an empty record
        namedata = NameData()

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
        tags=['masc'],
        source='wikipedia_en:Akifumi Endo',
    ), 'extracts gender from category'


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
        tags=['masc'],
        source='wikipedia_en:Akihiro Murata',
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
        tags=['masc'],
        source='wikipedia_en:Junya Kato',
    ), 'should not convert to じゅにゃ'
