from typing import cast
from yomikun.utils.romaji import romaji_to_hiragana

import regex
import jcconv3
import pytest

from yomikun.models import NameData
from yomikun.utils.patterns import name_pat
from yomikun.utils.split import split_kana_name
from yomikun.utils.romaji import romaji_to_hiragana_fullname


def parse_researchmap(kana: str, kanji: str, english: str) -> NameData:
    """
    Parse a researchmap card (kana, kanji, english fields) and return
    a NameData object. The NameData object may be empty if the input was
    not a Japanese name.

    Raises NotImplementedError for inputs we don't yet understand.
    """

    """
    Formats:
     - kana, kanji (w/ spaces), english [in caps or not]
     - kana is sometimes missing or ==kanji or ==romaji reversed, have to use romaji
       - romaji is sometimes reverse order

     - Chinese names are difficult: ['', '徐 ぎゅう', 'Qiu Xu']  ['', '李 鯤', 'Kun Li']
     - Many other errors, e.g. '望 岡亮介       望岡 亮介       Ryosuke Mochioka'
     - Romaji conversion is hard
       加来 洋 Yo Kaku        (=you)
       伊藤 桃代  Momoyo Ito  (=itou)
       井草 剛 IGUSA GO       (=gou)

     - Romaji dash: ヤマシタ ヨウイチ       山下 洋市       YO-ICHI YAMASHITA
       also used as a '
       タダキ シンイチ 只木 進一       Shin-ichi TADAKI
    """
    kanji_ok = regex.fullmatch(name_pat, kanji)
    if not kanji_ok:
        # Records without kanji in the second field are generally non-Japanese
        return NameData()

    # Convert half-width
    kana = cast(str, jcconv3.half2hira(kana))

    # Easy case
    # TODO no space, hiragana also common
    if regex.match(r'^\p{Katakana}+\s+\p{Katakana}+$', kana):
        kana = cast(str, jcconv3.kata2hira(kana))
        return NameData(kanji, kana)
    elif regex.match(r'^\p{Katakana}+$', kana):
        # Katakana name with no space
        kana = cast(str, jcconv3.kata2hira(kana))
        kana = split_kana_name(kanji, kana)
        if len(kana.split()) == 2:
            # Successful
            return NameData(kanji, kana)
    elif regex.match(r'^[a-z]+\s+[a-z]+', kana):
        # Romaji, in correct order (presumably)
        if new_kana := romaji_to_hiragana_fullname(kana, kanji):
            return NameData(kanji, new_kana)

    elif regex.match(r'^\p{Hiragana}\s+\p{Hiragana}+$', kana):
        return NameData(kanji, kana)

    raise NotImplementedError("don't know how to handle this")


tests = [
    # (kana, kanji, english), expected_kaki, expected_yomi
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
    (('イガラシリョウスケ',	'五十嵐 涼介', 'Ryosuke IGARASHI'), '五十嵐 涼介', 'いがらし りょうすけ'),
    (('アダチシンイチ',	'足立 慎一', 'SHINICHI ADACHI'), '足立 慎一', 'あだち しんにち'),
    # No space, only part of name
    (('イシイ', '石井 浩二', 'Koji Ishii'), '石井 浩二', 'いしい こうじ'),
    (('ウスクラ', '臼倉 孝弘', 'takahiro usukura'), '臼倉 孝弘', 'うすくら たかひろ'),
    # Half-width
    (('ｶｻﾏﾂ ﾀﾞｲｽｹ', '笠松 大佑', 'Daisuke Kasamatsu'), '笠松 大佑', 'かたまつ だいすけ'),
    (('ｶﾈｺ ｶｽﾞﾖｼ', '金子 和義', 'Kazuyoshi Kaneko'), '金子 和義', 'かねこ かずよし'),
    # Not sure what these are.
    (('no date', '高尾 健司', 'no date'), '', ''),
    (('no data', '辻 一成', 'no data'), '', ''),
    # Romaji
    (('Nohara Takahiro', '野原 隆弘', 'Takahiro Nohara'), '野原 隆弘', 'のはら たかひろ'),
    (('', '一之瀬 敦幾', 'Atsuki ICHINOSE'), '一之瀬 敦幾', 'いちのせ あつき'),
    (('', '坪山 直生', 'Tadao Tsuboyama'), '坪山 直生', 'つぼやま ただお'),
    # Romaji, but some vowels need lengthening
    (('Nozaki Yuji', '野﨑 祐史', 'Yuji Nozaki'), '野﨑 祐史', 'のざき ゆうじ'),
    (('FUSE KYOKO', '布施 香子', 'Fuse Kyoko'), '布施 香子', 'ふせ きょうこ'),
    (('AZUMA YUTARO', '東 祐太郎', 'Azuma Yutaro'), '東 祐太郎', 'あずま ゆうたろう'),
    # Wrong order
    (('Yuki Ohashi', '大橋 祐紀'), '大橋 祐紀', 'おおはし ゆうき'),
    # Romaji, with -
    (('Murata Ken-ichiro', '村田 憲一郎', 'Ken-ichiro Murata'), '村田 憲一郎', 'むらた けんいちろう'),
    # 小河 can be read as おご or おごう, in this case the 'oh' implies おごう
    (('Ogoh Shigehiko', '小河 繁彦', 'Shigehiko Ogoh'), '小河 繁彦', 'おごう しげひこ'),
    (('Ohji Masahito', '大路 正人', 'Masahito Ohji'), '大路 正人', 'おおじ まさひと'),
    # Non-Japanese
    (('PARK Yoosung', '朴 堯星', 'Yoosung PARK'), '', ''),
    (('パクヘビン', '朴 蕙彬', 'PARK HYEBIN'), '', ''),
    (('イー ゴアンホ', '李 光鎬', 'Lee Kwangho'), '李 光鎬', 'いー ごあんほ'),
    (('Cao Wenjing', '曹 文静', 'CAO WENJING'), '', ''),
    (('Liang Naishen', '梁 乃申', 'Naishen Liang'), '', ''),
]


@ pytest.mark.parametrize('test', tests)
def test_parse_researchmap(test):
    test_args, expected_kaki, expected_yomi = test
    result = parse_researchmap(*test_args)
    assert result == NameData(expected_kaki, expected_yomi)
