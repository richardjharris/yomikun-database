"""
Utilities for ignoring invalid names from Wikipedia articles
"""
from yomikun.models import NameData

import regex

"""Ignore names containing these words"""
ignore_words = [
    '道の駅',
    '学校',
    '地球',
    '組合',
]
ignore_words_pat = regex.compile(r"\L<words>", words=ignore_words)


"""
Name lengths are approx 10% 2 chars, 15% 3, 40% 4,
28% 5, 6% 6, 0.1% 7.

There are a handful of legally registered names
beyond 7 chars, e.g.

NODA Egawa-fuji-hifumishigo-zaemon-no-suketarou
野田　江川富士一二三四五左衛門助太郎

The longest name of somebody currently alive is 11:

藤本　太郎喜左衛門將時能

A few examples of 10 character names:

燕東 海林太郎兵衛宗清
根本 寝坊之助食左衛門

Most forms have a maximum of 6 or 7, so we can probably
exclude anything beyond that.
"""
max_total_name_length = 7

"""
Family names are typically 2 or 3. There are some very
rare family names:

勘解由小路 (かでのこうじ) 10 people
左衛門三郎 (さえもんさぶろう) 1 person
釈迦牟尼仏 (みくるべ) ~240 people at one time?
There is a rugby player called 源五郎丸 洋 (げんごろうまる　ひろし)

etc (see https://name.sijisuru.com/Columns/longname)
"""
max_family_name_length = 5


# TODO handle logging here?
# TODO ignore yomi=の
def should_ignore_name(kaki: str) -> bool:
    sei, mei = kaki.split()
    if len(sei) > max_family_name_length:
        return True
    elif len(sei) + len(mei) >= max_total_name_length:
        return True
    elif ignore_words_pat.match(sei):
        return True
    elif ignore_words_pat.match(mei):
        return True
    else:
        return False
