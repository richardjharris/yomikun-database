from __future__ import annotations
from operator import itemgetter
from typing import cast
import logging

import regex
import jcconv3
import pytest
import romkan

from yomikun.models import NameData
from yomikun.utils.patterns import name_pat
from yomikun.utils.split import (
    split_kana_name,
    split_kanji_name,
    split_kanji_name_romaji,
)
from yomikun.utils.romaji import (
    romaji_to_hiragana_fullname,
    romaji_to_hiragana_fullname_parts,
)
from yomikun.utils.romaji.messy import romaji_to_hiragana_messy


def parse_researchmap(kana: str, kanji: str, english: str) -> NameData | None:
    """
    Parse a researchmap card (kana, kanji, english fields) and return
    a NameData object, or None if we know the input is not a Japanese
    name.
    """
    data = _parse_researchmap_inner(kana, kanji, english)
    if not data:
        return

    assert data.has_name()

    # Normalise spaces etc.
    data.clean()

    # Fix some common errors
    if data.kaki.startswith('金 ') and data.yomi.startswith('きm '):
        data.yomi = data.yomi.replace('きm', 'きん')

    data.yomi = data.yomi.replace('ヱ', 'ゑ')

    data.source = 'researchmap'
    data.add_tag('person')
    data.clean_and_validate()

    return data


def _parse_researchmap_inner(
    kana: str, kanji: str, english: str, swap_names: bool = True
) -> NameData | None:
    """
    This code does the hard work of figuring out what fields correspond to what name
    parts (if out of order), mapping romaji to kana, splitting kanji names that aren't
    split, reversing names if in reverse order.

    Romaji conversion is particularly hard due to ambiguities:
       加来 洋 Yo Kaku        (=you)
       伊藤 桃代  Momoyo Ito  (=itou)
       井草 剛 IGUSA GO       (=gou)
    We handle this by producing a RomajiDB that maps normalised romaji (e.g. all long
    vowels removed) and kanji to a list of possible kana names. This data is produced
    from reliable sources such as ja-wikipedia.

    If `swap_names` is True and we are using a romaji name where we don't know either
    of the parts, we try to swap the parts around. This is useful for cases where the
    romaji could either be 'Surname Forename' or 'Forename Surname'. However, we might
    generate a name in the wrong order. For sites like wikipedia where the romaji is
    usually in the correct order, `swap_names` should be set to False.
    """
    raw_data = (kana, kanji, english)
    logging.debug(f"Parsing {raw_data}")

    kana, kanji, english = (col.strip() for col in raw_data)

    kana = kana.lower()

    # Fix a common pattern of LastnameFirstname
    english = regex.sub(r'^([A-Z][a-z]+)([A-Z][a-z]+)$', r'\1 \2', english)
    # ... and firstnameLASTNAME
    english = regex.sub(r'^([A-Za-z][a-z]+)([A-Z]+)$', r'\2 \1', english)
    english = english.replace('ｰ', '-')
    english = english.lower()

    kanji_ok = regex.fullmatch(name_pat, kanji)
    if not kanji_ok:
        # Records without kanji in the second field are generally non-Japanese
        logging.debug("Rejecting (not kanji_ok)")
        return

    # Convert half-width
    if kana:
        kana = cast(str, jcconv3.half2hira(kana))

    # Hack for tenten. There are only a handful of these in the input, so we don't
    # need to consider all of them.
    kana = kana.replace('ス゛', 'ズ').replace('タ゛', 'ダ').replace('シ゛', 'ジ')
    kana = kana.replace('カ゛', 'ガ').replace('ウ゛', 'ヴ')

    if kana in ('no data', 'no date'):
        # These records never contain any readings.
        logging.debug("Rejecting (no data)")
        return

    if regex.match(r'^\p{Hiragana}+\s+\p{Hiragana}+$', kana):
        # Most common case: kana is as expected
        kanji = split_kanji_name(kanji, kana)
        return NameData(kanji, kana)

    elif regex.match(
        r'^[\p{Katakana}\p{Hiragana}ー]+\s+[\p{Katakana}\p{Hiragana}ー]+$', kana
    ):
        # Convert katakana to hiragana
        # Allow a mixture. In particular hiragana へ・べ can appear in katakana text
        # because they look the same.
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
        return

    # If both fields are romaji then the 'kana' entry tends to be
    # in Japanese name order while the 'english' entry tends to be
    # in Western order.
    # Candidates are ordered most important to least.
    if swap_names:
        romaji_candidates = [
            kana,
            reverse_parts(english),
            reverse_parts(kana),
            english,
        ]
    else:
        romaji_candidates = [kana, english]

    romajis = []
    for romaji in romaji_candidates:
        if (
            regex.match(r'^[a-zāâīīîūûêēōôô\-]+\s+[a-zāâīīîūûêēōôô\-]+$', romaji)
            and romaji not in romajis
        ):
            romajis.append(romaji)

    logging.info(f"Got romajis: {romajis}")

    # Try with intelligent romaji to hiragana conversion
    for romaji in romajis:
        logging.info(f"Trying smart '{romaji}' for {kanji}")

        if regex.search(r'[[a-z]--[hmw]]', romkan.to_kana(romaji), regex.V1):
            # Could not convert to kana - probably a non-Japanese name.
            # (allow w (~ow), h as in 'oh', and 'm' (n).
            logging.debug("Rejecting (non-japanese name?)")
            return

        # May need to split the kanji (rare)
        new_kanji = split_kanji_name_romaji(kanji, romaji)
        logging.debug(f"Kanji is '{new_kanji}' after split")

        if new_kana := romaji_to_hiragana_fullname(romaji, new_kanji):
            return NameData(new_kanji, new_kana)

    # Try again with dumb conversion. This may produce incorrect results.
    # Keep track of each attempt and a 'score' representing how good we think
    # the attempt is; pick the best.
    attempts = []
    for romaji in romajis:
        warnings = []
        logging.info(f"Trying dumb '{romaji}' for {kanji})")
        bad = 0

        # May need to split the kanji (rare)
        kanji = split_kanji_name_romaji(kanji, romaji)
        logging.debug(f"Kanji is '{kanji}' after split")

        if len(kanji.split()) == 2:
            assert len(romaji.split()) == 2
            sei_kaki, mei_kaki = kanji.split()
            sei_roma, mei_roma = romaji.split()

            sei_kana, mei_kana = romaji_to_hiragana_fullname_parts(romaji, kanji)
            if sei_kana is None:
                warnings.append(
                    f"[{raw_data}] SEI ({sei_roma}, {sei_kaki}) was not in romajidb, "
                    "doing messy conversion"
                )
                sei_kana = romaji_to_hiragana_messy(sei_roma, sei_kaki)
                bad += 1
            if mei_kana is None:
                warnings.append(
                    f"[{raw_data}] MEI ({mei_roma}, {mei_kaki}) was not in romajidb, "
                    "doing messy conversion"
                )
                mei_kana = romaji_to_hiragana_messy(mei_roma, mei_kaki)
                bad += 1

            kana = f"{sei_kana} {mei_kana}"
            attempts.append((kana, bad, warnings))
        else:
            warnings.append(
                f"[{raw_data}] Entry ({romaji}, {kanji}) was not in romajidb "
                " (and unable to split), doing messy conversion"
            )
            kana = romaji_to_hiragana_messy(romaji, kanji)
            attempts.append((kana, 10, warnings))

    # Sort by 'bad'. As the sort is stable, the first item will be the earliest-ordered
    # candidate with the lowest 'bad' score.
    attempts.sort(key=itemgetter(1))
    if attempts:
        # if log level is DEBUG, print all attempts
        if logging.getLogger().getEffectiveLevel() >= logging.DEBUG:
            for attempt in attempts:
                logging.debug(f"Attempt: {attempt}")

        kana, _, warnings = attempts[0]
        for warning in warnings:
            logging.warning(warning)
        # TODO We tag xx-romaji even if only one part of the name was guessed; this
        #      can be fixed if we return 2 parts.
        return NameData(kanji, kana, tags={'xx-romaji'})

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
