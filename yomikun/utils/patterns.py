"""
Pattern for kanji characters used in surnames
"""
sei_chars = r'\p{Han}ヶヵノ'
sei_pat = fr'[{sei_chars}]+'

"""
Pattern for characters used in given names
"""
mei_pat = fr'[{sei_chars}' + r'\p{Hiragana}\p{Katakana}]+'

"""
Pattern for a full written name. We focus on names with kanji surnames.
"""
name_pat = fr'{sei_pat}\s*{mei_pat}'

hiragana_pat = r'\p{Hiragana}+'

"""
Pattern for a full name reading.
"""
reading_pat = fr'{hiragana_pat}\s+{hiragana_pat}'

"""
Name paren start
"""
name_paren_start = r'\s*+[（\(]\s*+'
