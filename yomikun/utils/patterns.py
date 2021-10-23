"""
Pattern for kanji characters used in surnames

 Interesting examples: 三ツ木 (みつぎ), 木ノ本
 茂り松 etc. are very rare, but interesting.
"""
sei_chars = r'\p{Han}ヶヵノツ'
sei_with_kana = r'(?:\p{Han}+[ツノ]\p{Han}+|茂り松|下り|走り|渡り|回り道|広エ|新タ|見ル野|反リ目|安カ川)'

sei_pat = fr'(?:[{sei_chars}]+|{sei_with_kana})'

"""
Pattern for characters used in given names
"""
mei_pat = fr'[{sei_chars}' + r'\p{Hiragana}\p{Katakana}ー]+'

"""
Pattern for a full written name. We focus on names with kanji surnames.
"""
name_pat = fr'{sei_pat}\s*{mei_pat}'

hiragana_pat = r'[\p{Hiragana}ー]+'

"""
Pattern for a full name reading.
"""
reading_pat = fr'{hiragana_pat}\s+{hiragana_pat}'

"""
Name paren start
"""
name_paren_start = r'\s*+[（\(]\s*+'
