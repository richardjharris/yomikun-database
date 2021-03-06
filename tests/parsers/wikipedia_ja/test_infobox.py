from yomikun.models import Lifetime, NameData
from yomikun.parsers.wikipedia_ja.infobox import (
    extract_infoboxes,
    extract_year,
    parse_infoboxes,
)


def test_extract_year():
    assert extract_year('[[1894年]][[4月29日]]') == 1894
    assert extract_year('{{死亡年月日と没年齢|1894|4|29|1946|1|30}}') == 1946
    assert extract_year('1990') == 1990
    assert extract_year('{{生年月日と年齢|1973|02|14}}') == 1973
    assert extract_year('<!-- {{死亡年月日と没年齢|XXXX|XX|XX|YYYY|YY|YY}} -->') is None
    assert extract_year('[[1894年]]') == 1894


def test_basic():
    text = """
<!-- some comments -->
{{政治家
|人名 = 安倍 寛
|各国語表記 = あべ かん
|生年月日 = [[1894年]][[4月29日]]
|没年月日 = {{死亡年月日と没年齢|1894|4|29|1946|1|30}}
}}
"""

    result = extract_infoboxes(text)
    assert len(result) == 1
    assert result[0].name == "政治家"
    assert result[0].data == {
        '人名': '安倍 寛',
        '各国語表記': 'あべ かん',
        '生年月日': '[[1894年]][[4月29日]]',
        '没年月日': '{{死亡年月日と没年齢|1894|4|29|1946|1|30}}',
    }

    parsed = parse_infoboxes(result)
    assert parsed == NameData(
        kaki='安倍 寛',
        yomi='あべ かん',
        lifetime=Lifetime(1894, 1946),
    )


def test_two():
    text = """
{{基礎情報 アナウンサー
|名前		= 松嶋 あすか
|ふりがな	= まつしま あすか
|生年月日	= {{生年月日と年齢|1973|02|14}}
|没年月日	= <!-- {{死亡年月日と没年齢|XXXX|XX|XX|YYYY|YY|YY}} -->
}}
"""
    result = extract_infoboxes(text)
    assert len(result) == 1
    assert result[0].name == "基礎情報 アナウンサー"
    assert result[0].data == {
        '名前': '松嶋 あすか',
        'ふりがな': 'まつしま あすか',
        '生年月日': '{{生年月日と年齢|1973|02|14}}',
        '没年月日': '<!-- {{死亡年月日と没年齢|XXXX|XX|XX|YYYY|YY|YY}} -->',
    }

    parsed = parse_infoboxes(result)
    assert parsed == NameData(
        kaki='松嶋 あすか',
        yomi='まつしま あすか',
        lifetime=Lifetime(1973),
    )


def test_multi():
    text = """
{{foo
| a = 1
| b = 2
}}
Some other stuff
blah
{{bar
| c = 3
| d = 4
| 生年 = 1960
}}

End"""

    result = extract_infoboxes(text)
    assert len(result) == 2
    assert result[0].name == "foo"
    assert result[0].data == {'a': '1', 'b': '2'}
    assert result[1].name == 'bar'
    assert result[1].data == {'c': '3', 'd': '4', '生年': '1960'}

    parsed = parse_infoboxes(result)
    assert parsed.lifetime == Lifetime(1960), 'examined both boxes'


def test_abe_hiroshi():
    abe = """
{{ActorActress<!-- テンプレートは変更しないでください。「Template:ActorActress」参照 -->
| 芸名 = 阿部 寛
| ふりがな = あべ ひろし
| 画像ファイル = Abe Hiroshi from "Legend of the Demon Cat" at Opening Ceremony of the Tokyo International Film Festival 2017 (40203798571).jpg
| 画像サイズ = 230px
| 画像コメント =
| 本名 =
| 別名義 = <!-- 別芸名がある場合記載。愛称の欄ではありません。 -->
| 出生地 = {{JPN}}・[[神奈川県]][[横浜市]][[神奈川区]]
| 死没地 =
| 国籍 =日本
| 身長 = 189 [[センチメートル|cm]]
| 血液型 = [[ABO式血液型|A型]]
| 生年 = 1964
| 生月 = 6
| 生日 = 22
| 没年 =
| 没月 =
| 没日 =
| 職業 = [[俳優]]・[[モデル (職業)|モデル]]
| ジャンル = [[映画]]・[[テレビドラマ]]・[[舞台]]・[[ファッション]]
| 活動期間 = [[1983年]] -
| 活動内容 = [[1983年]]：モデルデビュー<br />[[1983年]]：コンテストで優勝<br />[[1987年]]：俳優デビュー
| 配偶者 = [[既婚]]<!--2008年-->
| 著名な家族 =
| 事務所 = [[茂田オフィス]]
| 公式サイト = [http://abehiroshi.la.coocan.jp/ 阿部寛のホームページ]
| 主な作品 = '''テレビドラマ'''<br />『[[トリック (テレビドラマ)|TRICK]]』シリーズ<br />『[[HERO (テレビドラマ)|HERO]]』<br />『[[できちゃった結婚 (テレビドラマ)|できちゃった結婚]]』<br />『[[最後の弁護人]]』<br />『[[アットホーム・ダッド]]』<br />『[[ドラゴン桜 (テレビドラマ)|ドラゴン桜]]』シリーズ<br />『[[結婚できない男]]』シリーズ<br/>『[[CHANGE (テレビドラマ)|CHANGE]]』<br />『[[天地人 (NHK大河ドラマ)|天地人]]』<br/>『[[白い春]]』<br />『[[坂の上の雲 (テレビドラマ)|坂の上の雲]]』<br />『[[新参者 (小説)|新参者]]』<br />『[[下町ロケット (TBSのテレビドラマ)|下町ロケット]]』シリーズ<br />『[[スニッファー ウクライナの私立探偵#日本版|スニッファー 嗅覚捜査官]]』<hr />'''映画'''<br />『[[姑獲鳥の夏]]』<br />『[[バブルへGO!! タイムマシンはドラム式|バブルへGO!!]]』<br />『[[大帝の剣]]』<br />『[[自虐の詩]]』<br />『[[青い鳥 (2008年の映画)|青い鳥]]』<br />『[[歩いても 歩いても]]』<br />『[[トリック劇場版]]』<br />『[[ステキな金縛り]]』<br />『[[テルマエ・ロマエ]]』シリーズ<br />『[[麒麟の翼]]』シリーズ <br />『[[ふしぎな岬の物語]]』<br />『[[柘榴坂の仇討]]』<br />『[[海よりもまだ深く]]』<hr />'''声の出演'''<br />『[[真救世主伝説 北斗の拳]]』
| ブルーリボン賞 = '''主演男優賞'''<br />[[ブルーリボン賞 (映画)#第51回（2008年度） - 第60回（2017年度）|2012年]]『[[麒麟の翼#映画|麒麟の翼 〜劇場版・新参者〜]]』『テルマエ・ロマエ』『[[カラスの親指]]』
| ローレンス・オリヴィエ賞 =
| 全米映画俳優組合賞 =
| トニー賞 =
| 日本アカデミー賞 = '''最優秀主演男優賞'''<br />[[第36回日本アカデミー賞|2012年]]『[[テルマエ・ロマエ#映画|テルマエ・ロマエ]]』<br />'''優秀助演男優賞'''<br />[[第38回日本アカデミー賞|2014年]]『[[柘榴坂の仇討]]』
| その他の賞 = '''[[毎日映画コンクール]]'''<br /> '''男優主演賞'''<br />[[2008年]]『[[青い鳥 (2008年の映画)|青い鳥]]』『[[歩いても歩いても]]』<hr />'''[[ヨコハマ映画祭]]'''<br /> '''主演男優賞'''<br />[[2012年]]『テルマエ・ロマエ』<hr />'''[[京都国際映画祭]]'''<br />2016年 [[三船敏郎]]賞
| 備考 =
}}
{{男性モデル
|モデル名= 阿部 寛
|ふりがな= あべ ひろし
|画像ファイル=
|別名=
|愛称= 阿部ちゃん
|生年= 1964
|生月= 6
|生日= 22
|出身地= {{JPN}} [[神奈川県]][[横浜市]][[神奈川区]]
|血液型= [[ABO式血液型|A型]]
|身長= 189
|デビュー= [[1983年]]
|ジャンル= [[映画]]、[[テレビドラマ]]、[[舞台]]、[[ファッション]]
|モデル内容= 一般
|活動備考=
|他の活動= [[俳優 ]]、[[モデル (職業)|モデル]]
|その他=
}}
'''阿部 寛'''（あべ ひろし、[[1964年]]〈昭和39年〉[[6月22日]]<ref name="rirekisho" /> - ）は、[[日本]]の[[俳優]]。[[茂田オフィス]]所属。
"""  # noqa
    boxes = extract_infoboxes(abe)
    parsed = parse_infoboxes(boxes)
    assert parsed == NameData(
        kaki='阿部 寛',
        yomi='あべ ひろし',
        lifetime=Lifetime(1964),
    )
