import regex

from yomikun.models import NameData
from yomikun.utils.patterns import name_paren_start, name_pat, reading_pat
from yomikun.utils.split import split_kanji_name

"""
Some examples:
'''森 哲郎'''（もり てつろう、[[1928年]] - [[2008年]][[7月9日]]）は[[日本]]の[[漫画家]]。[[愛知県]][[名古屋市]]出身。本名は正衛（＝まさもり）。
'''巧 舟'''（たくみ しゅう<!--生年月日を記載する場合は出典を用いてください-->）は、[[カプコン]]に所属する[[日本]]の[[ゲームクリエイター]]。本名同じ (infobox: 本名 = 同じ) also
   ... 巧」が[[姓]]、「舟」が[[名前]]である。ペンネームのようだが本名

'''山藤 一郎'''（ふじやま いちろう、[[1911年]]（[[明治]]44年）[[4月8日]] - [[1993年]]（[[平成]]5年）[[8月21日]]）は、... 本名、増永 丈夫（ますなが たけお）。
'''アイ・ジョージ'''（[[1933年]][[9月27日]] - ）は[[日本]]の元[[歌手]]、[[俳優]]。本名、'''石松 譲冶'''（いしまつ じょうじ）。

本名は阿部寛（あべひろし）   (same as real name. infobox has empty section for 本名)

# Not currently parsed
'''山崎 哲'''（やまざき てつ、[[1946年]][[6月21日]] - ）は、日本の劇作家、評論家。本名・渡辺康徳。
"""  # noqa

# Patterns indicating that the article subject is using a pseudonym, with the real
# name after.
honmyo_pats = [
    regex.compile(
        fr"本名(?:・旧芸名)?(?:は、?|、|\s|：|・)\s*({name_pat})\s*{name_paren_start}({reading_pat})[）\)、]"
    ),
    regex.compile(
        fr"本名(?:・旧芸名)?(?:は、?|、|\s|：|・)\s*'''({name_pat})'''{name_paren_start}({reading_pat})[）\)、]"
    ),
]


def find_honmyo(content: str) -> NameData | None:
    """
    Find honmyo (real name) indication from the article text.

    Return as a NameData, if it exists.
    """
    if content.find('本名') == -1:
        return None

    for pat in honmyo_pats:
        if m := pat.search(content):
            kaki, yomi = m.groups()
            kaki = split_kanji_name(kaki, yomi)
            subreading = NameData(kaki, yomi)
            return subreading

    return None
