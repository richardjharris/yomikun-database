"""
Pattern for kanji characters used in surnames
"""
sei_chars = r'\p{Han}ヶヵノ'

"""
Pattern for a full written name. We focus on names with kanji surnames.
"""
name_pat = fr'[{sei_chars}]+\s*[{sei_chars}' + r'\p{Hiragana}\p{Katakana}]+'

"""
Pattern for a full name reading.
"""
reading_pat = r'\p{Hiragana}+\s+\p{Hiragana}+'

"""
Name paren start
"""
name_paren_start = r'\s*+[（\(]\s*+'
