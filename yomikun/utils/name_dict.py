"""
Name dictionary used for making decisions like splitting a kanji
name into two halves.
"""
from yomikun.romajidb.db import romajidb
from yomikun.utils import jmnedict
from yomikun.utils.romaji.romaji_key import romaji_key


def match_name(kanji, kana, sei: bool, romaji=False) -> bool:
    """
    Returns bool indicating if the given name exists in our name
    dictionary.

    Assumes first name unless sei is True.

    For romaji data (romaji=True), uses the RomajiDB which handles
    ambiguous readings such as 'ryoma' for りょうま.

    For kana data, uses the JMNEdict database.
    """
    if romaji:
        romkey = romaji_key(kana)
        part = 'sei' if sei else 'mei'
        result = romajidb().get(kanji, romkey, part)
        if result:
            return True
    else:
        if sei:
            results = jmnedict.find_surname(kanji)
        else:
            results = jmnedict.find_given_name(kanji)

        for result in results:
            if kana in result.kana:
                return True

    return False
