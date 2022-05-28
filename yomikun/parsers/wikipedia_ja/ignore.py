"""
Utilities for ignoring invalid names from Wikipedia articles
"""
import regex

# Name lengths are approx: 10% 2 chars, 15% 3, 40% 4, 28% 5, 6% 6, 0.1% 7.
#
# There are a handful of legally registered names
# beyond 7 chars, e.g.:
# NODA Egawa-fuji-hifumishigo-zaemon-no-suketarou
# 野田　江川富士一二三四五左衛門助太郎
#
# The longest name of somebody currently alive is 11:
# 藤本　太郎喜左衛門將時能
#
# A few examples of 10 character names:
#
# 燕東 海林太郎兵衛宗清
# 根本 寝坊之助食左衛門
#
# However allowing these would allow in other false-positives, so we
# go with 7.
max_total_name_length = 7

# Ignore names containing these words
ignore_words = [
    '道の駅',
    '学校',
    '地球',
    '組合',
    '時代',  # suffix
    '大学',
    '大學',
    '女王',
    '幕府',
    '山脈',
    '庭園',
    '主義',
    '事件',
    '兵団',
]
ignore_words_pat = regex.compile(r"\L<words>", words=ignore_words)

# Family names are typically 2 or 3. There are some very
# rare longer family names:
#
# 勘解由小路 (かでのこうじ) 10 people
# 左衛門三郎 (さえもんさぶろう) 1 person
# 釈迦牟尼仏 (みくるべ) ~240 people at one time?
# There is a rugby player called 源五郎丸 洋 (げんごろうまる　ひろし)
#
# etc (see https://name.sijisuru.com/Columns/longname)
max_family_name_length = 5


def should_ignore_name(kaki: str) -> bool:
    sei, mei = kaki.split()
    if len(sei) > max_family_name_length:
        return True
    elif len(sei) + len(mei) >= max_total_name_length:
        return True
    elif ignore_words_pat.search(sei):
        return True
    elif ignore_words_pat.search(mei):
        return True
    elif regex.search(r"^.*の\s*[乱炎]$", kaki):
        return True
    else:
        return False


def test_ignore():
    assert should_ignore_name("上宮 高等学校"), 'mei contains 学校'
    assert should_ignore_name("李 施愛の乱"), 'ends 乱'
    assert should_ignore_name("飛騨 信用組合"), 'mei contains 組合'
    assert should_ignore_name("藤原是助の 乱"), 'ends 乱'
    assert should_ignore_name("欲望の 炎"), 'ends 炎'
    assert should_ignore_name("藤本　太郎喜左衛門將時能"), 'total length too long'
    assert should_ignore_name("何田神田の助 晃"), 'family name too long'
    assert should_ignore_name("高等学校 〇〇"), 'sei contains ignore word'


def test_allow():
    assert not should_ignore_name("田中 義明")
    assert not should_ignore_name("源五郎丸 洋")
