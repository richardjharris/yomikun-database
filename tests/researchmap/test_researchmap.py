import pytest

from yomikun.models.namedata import NameData
from yomikun.researchmap import parse_researchmap

tests = [
    # Format: (kana, kanji, english), expected_kaki, expected_yomi
    (('クドウ マサトシ', '工藤 正俊', 'Masatoshi Kudo'), '工藤 正俊', 'くどう まさとし'),
    (('', 'Browne Ryan', 'Ryan Browne'), '', ''),
    (('ドゥベイ アジット・クマール', 'Dubey Ajit Kumar', 'Ajit Kumar Dubey'), '', ''),
    # Wrong order
    (('小川 敬也', 'Ogawa Takaya', 'Takaya Ogawa'), '', ''),
    # Separate tenten
    (('イカ゛ラシ ヒデヤ', '五十嵐 英哉', 'Hideya Igarashi'), '五十嵐 英哉', 'いがらし ひでや'),
    # Hiragana
    (('いいづか しゅん', '飯塚 舜', 'Shun Iizuka'), '飯塚 舜', 'いいづか しゅん'),
    # No space
    (('イガラシリョウスケ', '五十嵐 涼介', 'Ryosuke IGARASHI'), '五十嵐 涼介', 'いがらし りょうすけ'),
    (('アダチシンイチ', '足立 慎一', 'SHINICHI ADACHI'), '足立 慎一', 'あだち しんいち'),
    # No space, only part of name
    (('イシイ', '石井 浩二', 'Koji Ishii'), '石井 浩二', 'いしい こうじ'),
    (('ウスクラ', '臼倉 孝弘', 'takahiro usukura'), '臼倉 孝弘', 'うすくら たかひろ'),
    # No space in kanji AND reverse order
    (('', '高木潤野', 'Junya Takagi'), '高木 潤野', 'たかぎ じゅんや'),
    # Half-width
    (('ｶｻﾏﾂ ﾀﾞｲｽｹ', '笠松 大佑', 'Daisuke Kasamatsu'), '笠松 大佑', 'かさまつ だいすけ'),
    (('ｶﾈｺ ｶｽﾞﾖｼ', '金子 和義', 'Kazuyoshi Kaneko'), '金子 和義', 'かねこ かずよし'),
    # Not sure what these are.
    (('no date', '高尾 健司', 'no date'), '', ''),
    (('no data', '辻 一成', 'no data'), '', ''),
    # Romaji
    (('Nohara Takahiro', '野原 隆弘', 'Takahiro Nohara'), '野原 隆弘', 'のはら たかひろ'),
    (('', '一之瀬 敦幾', 'Atsuki ICHINOSE'), '一之瀬 敦幾', 'いちのせ あつき'),
    (('', '坪山 直生', 'Tadao Tsuboyama'), '坪山 直生', 'つぼやま ただお'),
    (('', '田中 奈歩美', 'Nahomi Tanaka'), '田中 奈歩美', 'たなか なほみ'),
    # Romaji, but some vowels need lengthening
    (('Nozaki Yuji', '野﨑 祐史', 'Yuji Nozaki'), '野﨑 祐史', 'のざき ゆうじ'),
    (('FUSE KYOKO', '布施 香子', 'Fuse Kyoko'), '布施 香子', 'ふせ きょうこ'),
    (('AZUMA YUTARO', '東 祐太郎', 'Azuma Yutaro'), '東 祐太郎', 'あずま ゆうたろう'),
    # Wrong order
    (('Yuki Ohashi', '大橋 祐紀', ''), '大橋 祐紀', 'おおはし ゆうき'),
    # Wrong order, missing vowels
    (('', '北條 良介', 'hojo ryosuke'), '北條 良介', 'ほうじょう りょうすけ'),
    # Romaji, with -
    (('Murata Ken-ichiro', '村田 憲一郎', 'Ken-ichiro Murata'), '村田 憲一郎', 'むらた けんいちろう'),
    # 小河 can be read as おご or おごう, in this case the 'oh' implies おごう. We need frequency
    # data to pick the right one.
    (('Ogoh Shigehiko', '小河 繁彦', 'Shigehiko Ogoh'), '小河 繁彦', 'おごう しげひこ'),
    (('Ohji Masahito', '大路 正人', 'Masahito Ohji'), '大路 正人', 'おおじ まさひと'),
    # Non-Japanese
    (('PARK Yoosung', '朴 堯星', 'Yoosung PARK'), '', ''),
    (('パクヘビン', '朴 蕙彬', 'PARK HYEBIN'), '', ''),  # no idea how this passes
    (('イー ゴアンホ', '李 光鎬', 'Lee Kwangho'), '李 光鎬', 'いー ごあんほ'),
    (('Cao Wenjing', '曹 文静', 'CAO WENJING'), '', ''),
    (('Liang Naishen', '梁 乃申', 'Naishen Liang'), '', ''),
    # SurnameFirstname style
    (('', '真島 綾子', 'MashimaAyako'), '真島 綾子', 'ましま あやこ'),
    (('', '清水 典孝', 'noritakaSHIMIZU'), '清水 典孝', 'しみず のりたか'),
    # handle 'oh' as long o
    (('', '大石 侑香', 'Yuka OISHI'), '大石 侑香', 'おおいし ゆうか'),
    (('', '大石 勝', 'Masaru Ohishi'), '大石 勝', 'おおいし まさる'),
    (('', '大井 駿', 'Shun Ohi'), '大井 駿', 'おおい しゅん'),
    (('', '大橋 千恵', 'Chie Ohashi'), '大橋 千恵', 'おおはし ちえ'),
    # handle 'uh' as long u
    (('', '清水 裕也', 'Yuhya Shimizu'), '清水 裕也', 'しみず ゆうや'),
    # Kana べ - should still use kana, not romaji
    (('クサカべ スメジ', '日下部 寿女士', 'Sumeji Kusakabei'), '日下部 寿女士', 'くさかべ すめじ'),
    # Even if we don't know one name part, we should properly romanize the other.
    # e.g. this should be ごとう not ごと.
    (('', '後藤 云々真間', 'Shikajikamama Goto'), '後藤 云々真間', 'ごとう しかじかまま'),
    (('', '後藤 云々真間', 'Goto Shikajikamama'), '後藤 云々真間', 'ごとう しかじかまま'),
    (('', '云々真間 侑香', 'Yuka Shikajikamama'), '云々真間 侑香', 'しかじかまま ゆうか'),
    (('', '云々真間 侑香', 'Shikajikamama Yuka'), '云々真間 侑香', 'しかじかまま ゆうか'),
    # Hyphens!
    (('', '寺澤 知潮', 'Tomo-o Terasawa'), '寺澤 知潮', 'てらさわ ともお'),
    (('', '田中 雅篤', 'Masa-atsu Tanaka'), '田中 雅篤', 'たなか まさあつ'),
    (('', '大洞 将嗣', 'Oh-hora Masatsugu'), '大洞 将嗣', 'おおほら まさつぐ'),
    (('', '廣瀬 貴章', 'Taka-aki Hirose'), '廣瀬 貴章', 'ひろせ たかあき'),
    (('', '木村 善一郎', 'Kimura Zen-ichiro'), '木村 善一郎', 'きむら ぜんいちろう'),
    # mp/mb
    (('', '池 俊平', 'Shumpei IKE'), '池 俊平', 'いけ しゅんぺい'),
    (('', '神林 由美', 'Yumi Kambayashi'), '神林 由美', 'かんばやし ゆみ'),
    # apostrophe
    (("Sin'ya Ryoma", '新屋 良磨', "Ryoma Sin'ya"), '新屋 良磨', 'しんや りょうま'),
    (('', '古川 淳一朗', "Jun'ichiro Furukawa"), '古川 淳一朗', 'ふるかわ じゅんいちろう'),
    (('', '平田 統一', "Toh'ichi Hirata"), '平田 統一', 'ひらた とういち'),
]


@pytest.mark.parametrize('test', tests, ids=lambda x: x[0][1])
def test_parse_researchmap(test):
    test_args, expected_kaki, expected_yomi = test
    result = parse_researchmap(*test_args)

    if expected_yomi == '' and expected_kaki == '':
        assert result is None
    else:
        assert result is not None
        result.remove_xx_tags()
        assert result == NameData(
            expected_kaki, expected_yomi, source='researchmap', tags={'person'}
        )
