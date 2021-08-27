"""
Pattern for kanji characters used in surnames
"""
kanji_pat = r'[\p{Han}ヶヵ]'

"""
Pattern for a full written name. We focus on names with kanji surnames.
"""
name_pat = r'[\p{Han}ヶヵ]+\s*[\p{Han}ヶヵ\p{Hiragana}\p{Katakana}]+'

"""
Pattern for a full name reading.
"""
reading_pat = r'\p{Hiragana}+\s+\p{Hiragana}+'

"""
Name paren start
"""
name_paren_start = r'\s*+[（\(]\s*+'
