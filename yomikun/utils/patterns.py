"""
Pattern for kanji characters used in surnames

 Interesting examples: 三ツ木 (みつぎ), 木ノ本
 茂り松 etc. are very rare, but interesting.
"""
import regex

sei_chars = r'\p{Han}ケヶヵノツ'
_sei_with_kana = r"""
    (?:
     \p{Han}+[ツノ]\p{Han}+
    |茂り松|回り道|廻り道|見ル野|賀シ尾|反リ目|反り目|安カ川|烏ト根|沖ッ海
    |(?:下り|走り|渡り|広エ|新タ|下モ|乙め|五ッ|五ト|三ッ)\p{Han}?
    |\p{Han}の\p{Han}
    |一[つっッ]\p{Han}
    )
"""
sei_with_kana = regex.sub(r'\s+', '', _sei_with_kana)

sei_pat = fr'(?:[{sei_chars}]+|{sei_with_kana})'

"""
Pattern for characters used in given names
"""
mei_pat = fr'[{sei_chars}' + r'\p{Hiragana}\p{Katakana}ー]+'

"""
Pattern for a full written name. We focus on names with kanji surnames.

Space is optional.
"""
name_pat = fr'{sei_pat}\s*{mei_pat}'

"""
Pattern for a full written name with required space.
"""
name_pat_with_space = fr'{sei_pat}\s+{mei_pat}'

hiragana_pat = r'[\p{Hiragana}ー]+'

"""
Pattern for a full name reading.
"""
reading_pat = fr'{hiragana_pat}\s+{hiragana_pat}'

"""
Pattern for a full name reading, optionally without a space
"""
reading_pat_optional_space = fr'{hiragana_pat}\s*{hiragana_pat}'

"""
Name paren start
"""
name_paren_start = r'\s*+[（\(]\s*+'
