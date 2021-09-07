from __future__ import annotations
import logging

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import Reading, NameData, NameAuthenticity, Lifetime
from yomikun.wikipedia_ja.ignore import should_ignore_name
from yomikun.wikipedia_ja.infobox import extract_infoboxes, parse_infoboxes
from yomikun.wikipedia_ja.honmyo import find_honmyo
from yomikun.utils.patterns import name_pat, reading_pat, name_paren_start
from yomikun.utils.split import split_kanji_name


def parse_article_text(title: str, content: str) -> NameData:
    """
    Parses the name/years out of the article text. This is fairly consistent across
    articles, e.g.

    '''山藤 一郎'''（ふじやま いちろう、[[1911年]]（[[明治]]44年）[[4月8日]] - [[1993年]]（[[平成]]5年）[[8月21日]]）は、[[日本]]の[[歌手]]・[[声楽#西洋音楽における声楽|声楽家]]・[[作曲家]]・[[指揮者]]。本名、増永 丈夫（ますなが たけお）。[[位階]]は[[従四位]]。本名では[[クラシック音楽]]の声楽家・[[バリトン]]歌手として活躍した。

    There are some irregularities, for example date may contain 元号 years.

    `title` is used for logging.
    """
    # To speed things up we limit how much of the document we search.
    excerpt = content[0:10_000]

    # Find 'real name is ...' -type sentences.
    honmyo = find_honmyo(excerpt)

    # Get name and following paragraph of text from the article heading.
    m = regex.search(
        fr"^'''({name_pat})'''{name_paren_start}({reading_pat})(.*?)(?:\n\n|\Z)", excerpt, regex.M | regex.S)

    if m:
        kaki, yomi, extra_raw = m.groups()
        yomi = yomi.replace('、', '')
        kaki = split_kanji_name(kaki, yomi)
        reading = NameData(kaki, yomi)
        logging.info(f"Got headline reading {reading}")
    elif honmyo:
        # Make the honmyo the main reading
        reading, honmyo = honmyo, None
        logging.info(f"No headline reading, using honymo {reading}")
        # Extract extra_raw from the article content, if possible
        # Quite often the name is Latin/Katakana and has no furigana reading,
        # so include the reading in the extra_raw.
        m = regex.search(
            fr"^'''.*?'''（(.*?)(?:\n\n|\Z)", excerpt, flags=regex.M | regex.S)
        extra_raw = m.group(1) if m else ''
    else:
        logging.info(f"[{title}] Could not find a reading, giving up")
        # Return empty data record to indicate failure
        return NameData()

    # Check content after name for year info
    extra = clean(extra_raw)
    extra = regex.sub(r'[,、]', '', extra).strip()
    # Don't match 2 digit years as these could be confused for Showa, Heisei etc
    if m := regex.search(r'(\d{3,4})年', extra):
        reading.lifetime.birth_year = int(m[1])

        if m := regex.search(r'- (\d{3,4})年', extra):
            reading.lifetime.death_year = int(m[1])
    else:
        # Heuristic match, might remove if it FPs
        #  - allow a bracket right after the year, e.g. [[天正]]12年（[[1584年]]）
        #  - don't match past the hiragana/DOB section, else we FP e.g.
        #    '''近藤 麻理恵'''（こんどう まりえ, [[1984年]][[10月9日]] - ）は、...
        #      ... [[2010年]]末に出版した著書は[[ミリオンセラー]]となった。
        #  - This should really be parsing matched parens.
        if m := regex.search(r'(\d{4})年[）)]?[^）)。]+?(\d{4})年', extra):
            birth = int(m[1])
            death = int(m[2])
            if 15 <= (death - birth) <= 100 and \
                    1000 <= birth <= 2500:
                reading.lifetime = Lifetime(birth, death)

    if regex.search(r'架空', extra_raw):
        reading.authenticity = NameAuthenticity.FICTIONAL
    elif honmyo:
        reading.add_subreading(honmyo)
        reading.authenticity = NameAuthenticity.PSEUDO

    reading.clean()
    return reading


def parse_wikipedia_article(title: str, content: str, add_source: bool = True) -> NameData:
    """
    Parse ja.wikipedia article for names/readings and return the primary one.
    (At some point, other extracted names may also be returned)
    If possible, lifespan information is also extracted.

    This examines both the article Infobox and an early line of text that
    contains the name in bold followed by the reading in round brackets.
    """
    box_data = parse_infoboxes(extract_infoboxes(content))
    article_data = parse_article_text(title, content)

    namedata = NameData.merge(box_data, article_data)

    if namedata.has_name():
        # Exclude certain names which are likely to not be people
        # Also exclude cases where we were unable to split the name
        if len(namedata.kaki.split()) == 1 or should_ignore_name(namedata.kaki):
            logging.info(
                f"[{title}] Name '{namedata.kaki}' matched ignore rules, skipping")
            # Remove all information except for source
            namedata = NameData()

    if add_source:
        namedata.source = f"wikipedia_ja:{title}"
    return namedata


def test_basic():
    content = """
{{ActorActress<!-- テンプレートは変更しないでください。「Template:ActorActress」参照 -->
| 生年 = 1964
}}
'''阿部 寛'''（あべ ひろし、[[1964年]]〈昭和39年〉[[6月22日]]<ref name="rirekisho" /> - ）は、[[日本]]の[[俳優]]。[[茂田オフィス]]所属。
""".strip()
    assert parse_wikipedia_article('foo', content) == NameData(
        kaki='阿部 寛',
        yomi='あべ ひろし',
        lifetime=Lifetime(1964),
        source='wikipedia_ja:foo',
    )


def test_ref_in_first_line():
    content = """
'''鈴置 洋孝'''（すずおき ひろたか、[[1950年]][[3月6日]]<ref name="kenproduction">{{Cite web|date=|url=blah}}</ref>
"""
    assert parse_wikipedia_article('bar', content) == NameData(
        kaki='鈴置 洋孝',
        yomi='すずおき ひろたか',
        lifetime=Lifetime(1950),
        source='wikipedia_ja:bar',
    )