from yomikun.models import Lifetime, NameData, NameAuthenticity
from yomikun.wikipedia_en.parser import parse_wikipedia_article


# TODO: xx-romaji could be omitted here due to the long o.
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
        tags={'xx-romaji', 'masc', 'person'},
        source='wikipedia_en:Akifumi Endo',
        notes='Voice actor',
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
        tags={'masc', 'person'},
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
        tags={'xx-romaji', 'masc', 'person'},
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
        tags={'masc', 'person'},
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
        tags={'person', 'fem'},
        notes='Fictional character in the Fatal Fury and The King of Fighters series of fighting games by SNK',
    )
