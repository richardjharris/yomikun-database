"""
Parser for Japanese Wikipedia articles.
"""


import logging

import regex
from mediawiki_dump.tokenizer import clean

from yomikun.models import Lifetime, NameAuthenticity, NameData
from yomikun.models.gender import Gender
from yomikun.models.name_position import NamePosition
from yomikun.parsers.wikipedia_en.parser import get_categories
from yomikun.parsers.wikipedia_ja.honmyo import find_honmyo
from yomikun.parsers.wikipedia_ja.ignore import should_ignore_name
from yomikun.parsers.wikipedia_ja.infobox import extract_infoboxes, parse_infoboxes
from yomikun.utils.patterns import name_paren_start, name_pat, reading_pat
from yomikun.utils.split import split_kanji_name


def parse_article_text(title: str, content: str) -> NameData:
    """
    Parses the name/years out of the article `content`. This is fairly consistent across
    articles, e.g.

    '''山藤 一郎'''（ふじやま いちろう、[[1911年]]（[[明治]]44年）[[4月8日]] - [[1993年]]（[[平成]]5年）[[8月21日]]）は、
    [[日本]]の[[歌手]]・[[声楽#西洋音楽における声楽|声楽家]]・[[作曲家]]・[[指揮者]]。本名、増永 丈夫（ますなが たけお）。
    [[位階]]は[[従四位]]。本名では[[クラシック音楽]]の声楽家・[[バリトン]]歌手として活躍した。

    There are some irregularities, for example, date may contain 元号 years.

    `title` is used for logging.
    """

    # To speed things up we limit how much of the document we search.
    excerpt = content[0:10_000]

    # Remove references entirely, they can appear anywhere and are not semantically useful
    excerpt = regex.sub('<ref>(.{1,1000}?)</ref>', '', excerpt)

    # Find 'real name is ...' -type sentences.
    honmyo = find_honmyo(excerpt)

    # Get name and following paragraph of text from the article heading.
    m = regex.search(
        fr"^'''({name_pat})'''{name_paren_start}({reading_pat})(.*?)(?:\n\n|\Z)",
        excerpt,
        regex.M | regex.S,
    )

    if m:
        kaki, yomi, extra_raw = m.groups()
        yomi = yomi.replace('、', '')
        yomi = regex.sub(r'\s+', ' ', yomi)

        # Handle names like 'みなもと の よりいえ'
        if yomi.endswith(' の'):
            logging.debug(
                f'{kaki=} {yomi=} Looks like middle name? Removing and retrying...'
            )
            if m := regex.search(fr'^({reading_pat})', yomi[:-2] + extra_raw):
                yomi = m[1]
                logging.debug(f'New yomi is {yomi}')
            else:
                logging.debug('Did not match after removing の, leaving as is')

        kaki = split_kanji_name(kaki, yomi)
        reading = NameData(kaki, yomi)
        logging.info(f"Got headline reading {reading}")
    elif honmyo:
        # Make the honmyo the main reading
        reading = honmyo
        logging.info(f"No headline reading, using honymo {reading}")
        # Extract extra_raw from the article content, if possible
        # Quite often the name is Latin/Katakana and has no furigana reading,
        # so include the reading in the extra_raw.
        m = regex.search(
            r"^'''.*?'''（(.*?)(?:\n\n|\Z)", excerpt, flags=regex.M | regex.S
        )
        extra_raw = m.group(1) if m else ''
    else:
        logging.info(f"[{title}] Could not find a reading, giving up")
        # Return empty data record to indicate failure
        return NameData()

    # Check content after name for year info
    extra = clean(extra_raw)
    extra = regex.sub(r'[,、]', '', extra).strip()
    # Don't match 2 digit years as these could be confused for Showa, Heisei etc
    # Avoid '? - 1984年' type constructs
    if m := regex.search(r'^[^-]*?(\d{3,4})年', extra):
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
            if 15 <= (death - birth) <= 100 and 1000 <= birth <= 2500:
                reading.lifetime = Lifetime(birth, death)

    # Look for gender declaration in the opening sentence.
    if regex.search(r'女性\s*。', extra) or '、女性、' in extra_raw:
        reading.gender = Gender.female
    elif regex.search(r'男性\s*。', extra) or '、男性、' in extra_raw:
        reading.gender = Gender.male

    # See 松本麻実, 長江麻美, 相沢真美,  山口真未, 華耀きらり
    # FPs: [[多摩美術大学]][[教授]]。妻は女優の[[とよた真帆]]
    #      [[奈良女子大学]][[名誉教授]]。
    #      長女は女優の[[長澤まさみ]]<ref>。
    #      向井 万起男（むかい まきお、1947年（昭和22年）6月24日 - ）は、日本の医学者（医学博士）、
    #        エッセイスト。専門は病理学。日本人初の女性飛行士、向井千秋の夫として知られる。
    if (
        m := regex.search(r'(女学校出身|日本の女性|、女優|、女性|女性\d{4}年)', extra)
    ) and not regex.search(r'教授', extra_raw):
        reading.gender = Gender.female

    # Look for 'fictional character' declarations
    if regex.search(r'架空', extra_raw):
        reading.authenticity = NameAuthenticity.FICTIONAL
    elif honmyo:
        # This logic is a bit tricky as the default authenticity 'REAL' can also
        # mean 'unknown'/'not determined yet'.
        if reading is not honmyo:
            reading.add_subreading(honmyo)
            reading.authenticity = NameAuthenticity.PSEUDO
    elif reading.authenticity == NameAuthenticity.REAL:
        # Double-check that there isn't an unparsed 本名 here
        # FP: '本名同じ', '「巧」が姓、「舟」が名前である。ペンネームのようだが本名[3]。通称は「タクシュー」[4]。'
        if m := regex.search(r'本名(.{0,4})', extra_raw):
            trailing = clean(m[1])
            logging.debug(f'Unparsed 本名 found (following text: [{trailing}])')
            if regex.search(r'(同じ|。)', trailing):
                logging.debug('Ignoring (looks like FP)')
            else:
                logging.debug('Marking PSEUDO')
                reading.authenticity = NameAuthenticity.PSEUDO

    reading.clean()
    return reading


def add_category_data(reading: NameData, content: str):
    """
    Extract categories from `content` and update `reading` in place
    with the parsed data (lifetime, gender, fictional character etc.)
    """
    # Check categories too
    for category in get_categories(content):
        # A blanket search for '女性' might cause false positives
        # Even 日本の女子 can be an FP e.g. if person is a coach
        if (
            regex.search(
                r'(ソプラノ歌手|日本の女性|日本の女子|女性(騎手|競輪選手)|女優$|中国の女性|女流棋士$|の女性$)', category
            )
            or category in ('グラビアアイドル', 'レースクイーン', '女院', '日本の尼僧', '女房名')
            or regex.search(r'^日本の女子.*選手$', category)
        ):
            if category != '日本の女子サッカー':
                reading.gender = Gender.female
        elif regex.search(r'(日本の男性|日本の男子)', category):
            reading.gender = Gender.male
        elif regex.search(r'(日本の男優)', category) and reading.gender != Gender.female:
            # There are some false positives here (or rather women performing male roles?)
            reading.gender = Gender.male

        if regex.search(r'架空の', category):
            reading.authenticity = NameAuthenticity.FICTIONAL

        if m := regex.search(r'^(\d+)年生$', category):
            reading.lifetime.birth_year = int(m[1])
        elif m := regex.search(r'^(\d+)年没$', category):
            reading.lifetime.death_year = int(m[1])
        elif category == '存命人物':
            reading.lifetime.death_year = None
        elif category == '生年不明':
            reading.lifetime.birth_year = None


def merge_namedata(box_data: NameData, article_data: NameData) -> NameData:
    # Prefer article data if it has 2 readings and box has one.
    if article_data.subreadings and not box_data.subreadings:
        result = article_data
        other = box_data
    # otherwise prefer box data
    elif box_data.has_name():
        result = box_data
        other = article_data
    else:
        result = article_data
        other = box_data

    # Check the other source for subreadings, but only if we don't have
    # any.
    if not result.subreadings:
        for extra in other.subreadings:
            result.add_subreading(extra)

    # Prefer lifetime from Infobox. Will be overriden by category
    if box_data.lifetime:
        result.lifetime = box_data.lifetime

    # Merge tags
    result.tags = set(box_data.tags).union(article_data.tags)

    return result


def parse_wikipedia_article(
    title: str, content: str, add_source: bool = True
) -> NameData | None:
    """
    Parse ja.wikipedia article for names/readings and return the primary one.
    (At some point, other extracted names may also be returned)
    If possible, lifespan information is also extracted.

    This examines both the article Infobox and an early line of text that
    contains the name in bold followed by the reading in round brackets.
    """
    if ':' in title:
        # 1,500+ Template/Talk/Project/User pages have extractable names
        logging.debug(f"Skipping '{title}' (not an article page)")
        return

    box_data = parse_infoboxes(extract_infoboxes(content)).clean()
    article_data = parse_article_text(title, content).clean()

    logging.debug(f'Box data: {box_data}')
    logging.debug(f'Article data: {article_data}')

    namedata = merge_namedata(box_data, article_data)

    add_category_data(namedata, content)

    if not namedata.has_name():
        return

    # Exclude certain names which are likely to not be people
    # Also exclude cases where we were unable to split the kanji
    if len(namedata.kaki.split()) == 1 or should_ignore_name(namedata.kaki):
        logging.info(f"[{title}] Name '{namedata.kaki}' matched ignore rules, skipping")
        return

    if add_source:
        namedata.source = f"wikipedia_ja:{title}"

    namedata.position = NamePosition.person
    for s in namedata.subreadings:
        s.position = NamePosition.person

    namedata.clean_and_validate()

    return namedata


def test_basic():
    content = """
{{ActorActress<!-- テンプレートは変更しないでください。「Template:ActorActress」参照 -->
| 生年 = 1964
}}
'''阿部 寛'''（あべ ひろし、[[1964年]]〈昭和39年〉[[6月22日]]<ref name="rirekisho" /> - ）は、[[日本]]の[[俳優]]。[[茂田オフィス]]所属。
""".strip()  # noqa
    assert parse_wikipedia_article('foo', content) == NameData.person(
        kaki='阿部 寛',
        yomi='あべ ひろし',
        lifetime=Lifetime(1964),
        source='wikipedia_ja:foo',
    )


def test_ref_in_first_line():
    content = """
'''鈴置 洋孝'''（すずおき ひろたか、[[1950年]][[3月6日]]<ref name="kenproduction">{{Cite web|date=|url=blah}}</ref>
"""  # noqa
    assert parse_wikipedia_article('bar', content) == NameData.person(
        kaki='鈴置 洋孝',
        yomi='すずおき ひろたか',
        lifetime=Lifetime(1950),
        source='wikipedia_ja:bar',
    )
