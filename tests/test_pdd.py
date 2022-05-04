from yomikun.models import NameData, Lifetime
from yomikun.pdd import name_from_entry


def test_parse_pdd():
    assert name_from_entry(
        "さんゆうてい　えんしょう【三遊亭　円生(６代)】",
        "いのうえ　ああ【井上　唖々】\n1878. 1.30(明治11) 〜 1923. 7.11(大正12)\n◇小説家・俳人。本名は精一、別号は九穂(キュウスイ)・玉山。名古屋生れ。\n",  # noqa: E501
    ) == NameData.person(
        kaki="三遊亭 円生",
        yomi="さんゆうてい えんしょう",
        lifetime=Lifetime(1878, 1923),
        source='pdd:さんゆうてい　えんしょう【三遊亭　円生(６代)】',
    )


def test_no_separated_name():
    assert name_from_entry(
        "ふじわらのあきらけいこ【藤原　明子】",
        "ふじわらのあきらけいこ【藤原　明子】《ふぢはらのあきらけいこ》\n 829(天長 6) 〜  900(昌泰 3)\n◇藤原良房(ヨシフサ)の娘・文徳天皇の女御。染殿后(ソメト゛ノノキサキ)とも呼ぶ。。\n",  # noqa
    ) == NameData.person(
        kaki="藤原 明子",
        yomi="ふじわら あきらけいこ",
        lifetime=Lifetime(829, 900),
        source='pdd:ふじわらのあきらけいこ【藤原　明子】',
    ), 'の removed'

    assert name_from_entry(
        "みなもとのたかあきら【源　高明】",
        "みなもとのたかあきら【源　高明】\n 914(延喜14) 〜  982(天元 5)\n◇平安中期の公卿。西宮左大臣(ニシノミヤ・サタ゛イシ゛ン)と称する。醍醐天皇の皇子、母は源唱の女周子。\n",  # noqa
    ) == NameData.person(
        kaki="源 高明",
        yomi="みなもと たかあきら",
        lifetime=Lifetime(914, 982),
        source='pdd:みなもとのたかあきら【源　高明】',
    )


def test_alternate_name():
    assert name_from_entry(
        "よさの　あきこ【与謝野　晶子(與謝野　晶子)】",
        "よさの　あきこ【与謝野　晶子(與謝野　晶子)】\n1878.12. 7(明治11) 〜 1942. 5.29(昭和17)\n◇明治〜昭和初期の詩人・歌人。\n",  # noqa
    ) == NameData.person(
        kaki="与謝野 晶子",
        yomi="よさの あきこ",
        lifetime=Lifetime(1878, 1942),
        source='pdd:よさの　あきこ【与謝野　晶子(與謝野　晶子)】',
        subreadings=[
            NameData("與謝野　晶子", "よさの あきこ"),
        ],
    ), 'alternate name form ignored'


def test_question_marks():
    assert name_from_entry(
        "つかごし　けんじ ????【塚越　賢爾】",
        "つかごし　けんじ ????【塚越　賢爾】\n1900(明治33) 〜 1943(昭和18)\n◇飛行機の機関士。\n{{w_61526}}朝日新聞航空部員\n",  # noqa
    ) == NameData.person(
        kaki="塚越 賢爾",
        yomi="つかごし けんじ",
        lifetime=Lifetime(1900, 1943),
        source='pdd:つかごし　けんじ ????【塚越　賢爾】',
    )


def test_bogus_reading():
    """Ensure the script does not die encountering a yomi ending in 子"""
    name_from_entry(
        "しらき　しづ子【素木　しづ子】",
        "しらき　しづ子【素木　しづ子】\n⇒素木しづ\n",
    )
