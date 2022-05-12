from yomikun.utils.romaji.romaji_key import remove_accents, romaji_key


def test_remove_accents():
    assert remove_accents("āâīīîūûêēōôô") == "aaiiiuueeooo"


def test_romaji_key():
    assert romaji_key('yuusuke') == romaji_key('yusuke')
    assert romaji_key("man'you") == romaji_key("manyou")
    assert romaji_key("goto") == romaji_key("gotou")
    assert romaji_key("otani") == romaji_key("ohtani")
    assert romaji_key("kireh") == romaji_key("kirei")
    assert romaji_key("takashi") != romaji_key("takeshi")
    assert romaji_key("gotou") != romaji_key("botou")
    assert romaji_key("Yūsuke") == romaji_key("yuusuke")
    assert romaji_key("Yûsuke") == romaji_key("yuusuke")
    assert romaji_key("ooi") != romaji_key("aoi")
    assert romaji_key("shiina") == romaji_key("shina")
    assert romaji_key('saitou') != romaji_key('satoiu')
    assert romaji_key('sito') != romaji_key('saito')
    assert romaji_key('satow') == romaji_key('satou')
    assert romaji_key('shumpei') == romaji_key('shunpei')
    assert romaji_key('kaili') == romaji_key('kairi')


def test_romaji_key_m():
    assert romaji_key('shimba') == romaji_key('shinba')
    assert romaji_key('homma') == romaji_key('honma')


def test_romaji_key_punct():
    assert romaji_key('tomo-o') == romaji_key('tomo')
    assert romaji_key("ken'ichi") == romaji_key('kenichi')


def test_romaji_key_h():
    assert romaji_key('kumanogoh') == romaji_key('kumanogou')
    assert romaji_key('kumanogou') == romaji_key('kumanogo')
    assert romaji_key('yuhsuke') == romaji_key('yuusuke')


def test_romaji_key_h_vowel():
    assert romaji_key('ohishi') == romaji_key('oishi')
    assert romaji_key('ohiwa') == romaji_key('oiwa')
    assert romaji_key('ohoka') == romaji_key('oooka')
    assert romaji_key('ohoka') == romaji_key('ōoka')
    assert romaji_key('ohori') == romaji_key('oori')


def test_romaji_key_ooue():
    # These names should compare equal as they are two ways of writing
    # the same thing.
    assert romaji_key('ōue') == romaji_key('ooue')
