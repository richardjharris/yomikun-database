from typing import cast

import regex
import jcconv3
import pytest
import romkan
import logging

from yomikun.models import NameData
from yomikun.utils.patterns import name_pat
from yomikun.utils.split import split_kana_name, split_kanji_name, split_kanji_name_romaji, try_to_swap_names
from yomikun.utils.romaji import romaji_to_hiragana_fullname, romaji_to_hiragana_messy, romaji_to_hiragana_fullname_parts


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
    logging.debug(f"Parsing {(kana, kanji, english)}")

    kana = kana.lower()

    # Fix a common pattern of LastnameFirstname
    english = regex.sub(r'^([A-Z][a-z]+)([A-Z][a-z]+)$', r'\1 \2', english)
    # ... and firstnameLASTNAME
    english = regex.sub(r'^([A-Za-z][a-z]+)([A-Z]+)$', r'\2 \1', english)
    english = english.lower()

    kanji_ok = regex.fullmatch(name_pat, kanji)
    if not kanji_ok:
        # Records without kanji in the second field are generally non-Japanese
        logging.debug("Rejecting (not kanji_ok)")
        return NameData()

    # Convert half-width
    if kana:
        kana = cast(str, jcconv3.half2hira(kana))

    # Hack for tenten. There are only a handful of these in the input, so we don't
    # need to consider all of them.
    kana = kana.replace('ス゛', 'ズ').replace('タ゛', 'ダ').replace('シ゛', 'ジ')
    kana = kana.replace('カ゛', 'ガ').replace('ウ゛', 'ヴ')

    if kana == 'no data' or kana == 'no date':
        # These records never contain any readings.
        logging.debug("Rejecting (no data)")
        return NameData()

    if regex.match(r'^\p{Hiragana}+\s+\p{Hiragana}+$', kana):
        # Most common case: kana is as expected
        kanji = split_kanji_name(kanji, kana)
        return NameData(kanji, kana)

    elif regex.match(r'^[\p{Katakana}ー]+\s+[\p{Katakana}ー]+$', kana):
        # Convert katakana to hiragana
        kana = cast(str, jcconv3.kata2hira(kana))
        kanji = split_kanji_name(kanji, kana)
        return NameData(kanji, kana)

    if regex.match(r'^\p{Katakana}+$', kana):
        # Katakana name with no space, try to split
        if len(kanji.split()) == 2:
            kana = cast(str, jcconv3.kata2hira(kana))
            kana = split_kana_name(kanji, kana)
            if len(kana.split()) == 2:
                # Successful
                return NameData(kanji, kana).add_tag('xx-split')

    if not regex.search('[a-z]', kana + english):
        # Neither field contains romaji
        logging.debug("Rejecting (no romaji)")
        return NameData()

    # If both fields are romaji then the 'kana' entry tends to be
    # in Japanese name order while the 'english' entry tends to be
    # in Western order.
    romajis = []
    for r in [kana, reverse_parts(english), reverse_parts(kana), english]:
        if regex.match(r'^[a-z\-]+\s+[a-z\-]+', r) and \
                r not in romajis:
            romajis.append(r)
    logging.info(f"Got romajis: {romajis}")

    # Try with intelligent romaji to hiragana conversion
    for romaji in romajis:
        logging.info(f"Trying smart '{romaji}' for {kanji}")

        if regex.search(r'[a-gi-z]', romkan.to_kana(romaji)):
            # Could not convert to kana - probably a non-Japanese name.
            # (allow h as in 'oh' - will be dealt with later)
            logging.debug("Rejecting (non-japanese name?)")
            return NameData()

        # May need to split the kanji (rare)
        new_kanji = split_kanji_name_romaji(kanji, romaji)
        logging.debug(f"Kanji is '{new_kanji}' After split")

        if new_kana := romaji_to_hiragana_fullname(romaji, new_kanji):
            return NameData(new_kanji, new_kana)

    if romajis:
        # Try again with dumb conversion. This may produce incorrect results.
        romaji = romajis[0]
        logging.info(f"Trying dumb '{romaji}' for {kanji}")

        # May need to split the kanji (rare)
        kanji = split_kanji_name_romaji(kanji, romaji)
        logging.debug(f"Kanji is '{kanji}' After split")

        if len(kanji.split()) == 2:
            sei, mei = romaji_to_hiragana_fullname_parts(romaji, kanji)
            missing = (sei is None, mei is None)
            logging.warning(
                f"Entry ({romaji}, {kanji}) was not in romajidb {missing=}, doing messy conversion")
        else:
            logging.warning(
                f"Entry ({romaji}, {kanji}) was not in romajidb (and unable to split), doing messy conversion")

        kana = romaji_to_hiragana_messy(romaji, kanji)

        # Since the messy method does not consult a dictionary, names may be
        # in the wrong order - try to swap if sensible.
        kanji, kana = try_to_swap_names(kanji, kana)

        return NameData(kanji, kana, tags=['xx-romaji'])

    raise NotImplementedError("don't know how to handle this")


def reverse_parts(s: str):
    return ' '.join(reversed(s.split()))


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
    (('アダチシンイチ',	'足立 慎一', 'SHINICHI ADACHI'), '足立 慎一', 'あだち しんいち'),
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
]


@ pytest.mark.parametrize('test', tests, ids=lambda x: x[0][1])
def test_parse_researchmap(test):
    test_args, expected_kaki, expected_yomi = test
    result = parse_researchmap(*test_args)
    result.remove_tag('xx-split')
    assert result == NameData(expected_kaki, expected_yomi)
