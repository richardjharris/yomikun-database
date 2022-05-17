import re
from dataclasses import dataclass

import pytest

KANJI_NUMBERS = '〇一二三四五六七八九'
KANJI_NUMBER_CHAR_CLASS = '[' + KANJI_NUMBERS + ']'
YEAR_MATCHER = re.compile(
    '^［(' + KANJI_NUMBER_CHAR_CLASS + '{3,4}|)〜(' + KANJI_NUMBER_CHAR_CLASS + '{3,4}|)］'
)


@dataclass
class BirthDeathYear:
    birth_year: int | None = None
    death_year: int | None = None

    def __bool__(self) -> bool:
        return self.birth_year is not None or self.death_year is not None


def convert_kanji_year(kanji: str) -> int:
    """
    Convert a string in kanji numerals into Arabic numerals (0-9).
    Throws a ValueError if an invalid char is encountered.
    """
    if len(kanji) == 0:
        raise ValueError('empty string')

    numbers = (str(KANJI_NUMBERS.index(n)) for n in kanji)
    return int(''.join(numbers))


def parse_birth_and_death_year(text: str) -> BirthDeathYear:
    """
    Parses the birth/death year found in Daijisen entries. In general this
    is simply ［BIRTH_YEAR〜DEATH_YEAR］ where both years are written in
    kanji numerals, however we also deal with as many variations as possible:

    ［？　〜(year)］、［？〜(year)］　-- unknown start
    ［(year)〜　］　　　　　　　　　　　-- still alive
    ［？〜一二五五ころ］               -- ~ころ to mean about'
    ［八六〜一六一］                   -- three digit

    Currently ignored:
     前三九〇ころ  (mae???)

     More than one generation... (ignored by parent code)
      いけのぼう‐せんこう【池坊専好】いけのバウセンカウ
      {{w_50225}}（初世）［一五四〇ころ〜一六二〇ころ］立花の名手。信長、秀吉の後援を得て池坊流を発展させた。{{w_50226}}（二世）［一五七五〜一六五八］立花の名人。法橋（ほつきよう）に叙任。後水尾（ごみずのお）院の親任を得て、宮廷で立花を指導した。多数の立花図を残した。

    """
    result = BirthDeathYear()

    try:
        line = text.splitlines()[1]
    except IndexError:
        return result

    line = line.replace('　', '')
    line = line.replace('ころ', '')
    line = line.replace('？', '')
    if m := YEAR_MATCHER.match(line):
        try:
            result.birth_year = convert_kanji_year(m[1])
        except ValueError:
            pass
        try:
            result.death_year = convert_kanji_year(m[2])
        except ValueError:
            pass

    return result


def test_convert_kanji_year():
    assert convert_kanji_year('一八八七') == 1887
    assert convert_kanji_year('一八〇二') == 1802
    assert convert_kanji_year('一九五六') == 1956
    assert convert_kanji_year('四三〇') == 430
    assert convert_kanji_year('二〇〇〇') == 2000

    with pytest.raises(ValueError):
        convert_kanji_year('')

    with pytest.raises(ValueError):
        convert_kanji_year('？')

    with pytest.raises(ValueError):
        convert_kanji_year('sausages')


def test_parse_birth_and_death_year():
    assert parse_birth_and_death_year(
        "アープ【Wyatt Berry Stapp Earp】\n［一八四八〜一九二九］米国の西部開拓時代のガンマン。"
    ) == BirthDeathYear(1848, 1929)

    assert parse_birth_and_death_year(
        "おおとも‐そうりん【大友宗麟】おほとも‐\n［一五三〇〜一五八七］戦国時代の武将。"
    ) == BirthDeathYear(1530, 1587)

    assert parse_birth_and_death_year(
        "あべ‐の‐よりとき【安倍頼時】\n［？　〜一〇五七］平安中期の陸奥の豪族。子の貞任・宗任と\n"
    ) == BirthDeathYear(None, 1057), 'birth unknown'

    assert parse_birth_and_death_year(
        "あまのや‐りへえ【天野屋利兵衛】‐リヘヱ\n［？〜一七二七］江戸中期の大坂商人。"
    ) == BirthDeathYear(None, 1727), 'birth unknown (variant)'

    assert parse_birth_and_death_year(
        "エリウゲナ【Johannes Scotus Eriugena】\n［八一〇ころ〜八七七ころ］アイルランド生まれの神学者・哲学者。"
    ) == BirthDeathYear(810, 877), '--koro'

    assert parse_birth_and_death_year("かんざんらくぼく【寒山落木】\n正岡子規の句集。") == BirthDeathYear(
        None, None
    ), 'no dates - not a name'
