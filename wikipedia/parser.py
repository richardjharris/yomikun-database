from __future__ import annotations

import regex
from mediawiki_dump.tokenizer import clean

from models import Reading, NameData, NameType, Lifetime
from wikipedia.infobox import extract_infoboxes, parse_infoboxes

# Pattern indicating article subject is a fictional character
fictional_pat = regex.compile(r'架空')

# Patterns indicating that the article subject is using a pseudonym, with the real
# name after.
# TODO space -> \s*
honmyo_pats = [
    regex.compile(
        r"本名は?、?(\p{Han}+ \p{Han}+)（(\p{Hiragana}+ \p{Hiragana}+)[）、]"),
    regex.compile(
        r"本名は?、?'''(\p{Han}+ \p{Han}+)'''（(\p{Hiragana}+ \p{Hiragana}+)[）、]"),
]


def parse_article_text(content: str) -> NameData | None:
    """
    Parses the name/years out of the article text. This is fairly consistent across
    articles, e.g.

    '''山藤 一郎'''（ふじやま いちろう、[[1911年]]（[[明治]]44年）[[4月8日]] - [[1993年]]（[[平成]]5年）[[8月21日]]）は、[[日本]]の[[歌手]]・[[声楽#西洋音楽における声楽|声楽家]]・[[作曲家]]・[[指揮者]]。本名、増永 丈夫（ますなが たけお）。[[位階]]は[[従四位]]。本名では[[クラシック音楽]]の声楽家・[[バリトン]]歌手として活躍した。

    There are some irregularities, for example date may contain 元号 years.
    """
    excerpt = content[0:10_000]

    # Quickly filter out articles without a name
    m = regex.search(
        r"^'''(\p{Han}+\s+[\p{Han}\p{Hiragana}\p{Katakana}]+)'''（(\p{Hiragana}+\s+\p{Hiragana}+)(.*)", excerpt, regex.MULTILINE)
    if not m:
        return

    kaki, yomi, extra_raw = m.groups()

    # Commas count as Hiragana
    yomi = yomi.replace('、', '')

    reading = NameData(kaki, yomi)

    # Check content after name
    # NOTE: \d{4} is important, else we may match Japanese dates (Reiwa, Heisei etc.)
    #       which are less consistently marked up
    extra = clean(extra_raw)
    extra = extra.replace('、', '').strip()
    if m := regex.match(r'^(\d{4})年', extra):
        reading.lifetime.birth_year = int(m[1])

        if m := regex.search(r'- (\d{4})年', extra):
            reading.lifetime.death_year = int(m[1])

    if fictional_pat.match(excerpt):
        reading.name_type = NameType.FICTIONAL
    elif regex.match(r'本名', excerpt):
        reading.name_type = NameType.PSEUDO
        for pat in honmyo_pats:
            if m := pat.match(excerpt):
                kaki, yomi = m.groups()
                # TODO this should probably clone the original
                subreading = NameData(kaki, yomi, name_type=NameType.REAL)
                reading.add_subreading(subreading)
                break

    return reading


def parse_wikipedia_article(content: str) -> NameData | None:
    """
    Parse ja.wikipedia article for names/readings and return the primary one.
    (At some point, other extracted names may also be returned)
    If possible, lifespan information is also extracted.

    This examines both the article Infobox and an early line of text that
    contains the name in bold followed by the reading in round brackets.
    """
    # First, try parsing the infobox
    # TODO: handle cases where we only have partial name info
    # TODO: sometimes we can only get the birth year from the infobox.
    boxdata = parse_infoboxes(extract_infoboxes(content))

    if boxdata.lifetime and boxdata.has_name():
        # We're done, return that
        return boxdata

    # Otherwise, parse the article content to extract missing data.
    # TODO clean this up
    reading = parse_article_text(content)
    if reading:
        if not reading.lifetime:
            reading.lifetime = boxdata.lifetime
        return reading

    # TODO replace with .merge() method

    # Give up
    return


def test_basic():
    content = """
{{ActorActress<!-- テンプレートは変更しないでください。「Template:ActorActress」参照 -->
| 生年 = 1964
}}
'''阿部 寛'''（あべ ひろし、[[1964年]]〈昭和39年〉[[6月22日]]<ref name="rirekisho" /> - ）は、[[日本]]の[[俳優]]。[[茂田オフィス]]所属。
""".strip()
    assert parse_wikipedia_article(content) == NameData(
        kaki='阿部 寛',
        yomi='あべ ひろし',
        lifetime=Lifetime(1964),
    )


def test_ref_in_first_line():
    content = """
'''鈴置 洋孝'''（すずおき ひろたか、[[1950年]][[3月6日]]<ref name="kenproduction">{{Cite web|date=|url=blah}}</ref>
"""
    assert parse_wikipedia_article(content) == NameData(
        kaki='鈴置 洋孝',
        yomi='すずおき ひろたか',
        lifetime=Lifetime(1950),
    )
