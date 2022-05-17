from yomikun.models import Lifetime, NameData
from yomikun.parsers.wikipedia_ja.parser import parse_wikipedia_article


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
