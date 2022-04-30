from yomikun.jmnedict.parser import parse
from yomikun.models import Lifetime, NameData


def test_basic():
    data = {
        "idseq": 5000254,
        "kanji": [{"text": "あき竹城"}],
        "kana": [{"text": "あきたけじょう", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [{"lang": "eng", "text": "Aki Takejou (1947.4-)"}],
                "name_type": ["person"],
            }
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person(
            "あき 竹城", "あき たけじょう", lifetime=Lifetime(1947), source="jmnedict"
        ),
    ]


def test_sumo():
    data = {
        "idseq": 2831743,
        "kanji": [{"text": "蒼国来栄吉"}],
        "kana": [{"text": "そうこくらいえいきち", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [
                    {
                        "lang": "eng",
                        "text": "Sōkokurai Eikichi (sumo wrestler from Inner Mongolia, 1984-)",
                    },
                    {"lang": "eng", "text": "Engketübsin"},
                ],
                "name_type": ["person"],
            }
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person(
            "蒼国来 栄吉", "そうこくらい えいきち", lifetime=Lifetime(1984), source="jmnedict"
        ),
    ]


def test_taira():
    data = {
        "idseq": 5629450,
        "kanji": [{"text": "平知盛"}],
        "kana": [{"text": "たいらのとももり", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [
                    {"lang": "eng", "text": "Taira No Tomomori (1151-1185.4.25)"}
                ],
                "name_type": ["person"],
            }
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person(
            "平 知盛", "たいら とももり", lifetime=Lifetime(1151, 1185), source="jmnedict"
        ),
    ]


def test_oumi():
    data = {
        "idseq": 5228414,
        "kanji": [{"text": "近江の君"}],
        "kana": [{"text": "おうみのきみ", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [
                    {"lang": "eng", "text": "Oumi no Kimi (Genji Monogatari)"}
                ],
                "name_type": ["person"],
            }
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person("近江 君", "おうみ きみ", source="jmnedict"),
    ]


def test_long_u():
    data = {
        "idseq": 5459611,
        "kanji": [{"text": "千の利休"}],
        "kana": [{"text": "せんのりきゅう", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [
                    {
                        "lang": "eng",
                        "text": "Sen no Rikyū (1522-1591) (founder of the Sen School of tea ceremony)",  # noqa
                    }
                ],
                "name_type": ["person"],
            },
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person(
            "千 利休", "せん りきゅう", lifetime=Lifetime(1522, 1591), source="jmnedict"
        ),
    ]


def test_given_name():
    data = {
        "idseq": 5102781,
        "kanji": [{"text": "愛"}],
        "kana": [{"text": "ゆき", "nokanji": 0}],
        "senses": [
            {"SenseGloss": [{"lang": "eng", "text": "Yuki"}], "name_type": ["fem"]}
        ],
    }
    result = parse(data)
    # Should ignore gender tag and add 'dict'
    assert result == [
        NameData("愛", "ゆき", tags={"given", "dict"}, source="jmnedict"),
    ]


def test_surname():
    data = {
        "idseq": 5301123,
        "kanji": [{"text": "斎藤"}],
        "kana": [{"text": "さいとう", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [{"lang": "eng", "text": "Saitou"}],
                "name_type": ["surname"],
            }
        ],
    }
    result = parse(data)
    assert result == [
        NameData("斎藤", "さいとう", tags={"surname", "dict"}, source="jmnedict"),
    ]


def test_multiple_entries():
    data = {
        "idseq": 5001664,
        "kanji": [{"text": "輝夜姫"}, {"text": "かぐや姫"}],
        "kana": [{"text": "かぐやひめ", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [
                    {
                        "lang": "eng",
                        "text": "Kaguya-Hime (main character of Taketori Monogatari)",
                    },
                    {"lang": "eng", "text": "Princess Kaguya"},
                ],
                "name_type": ["person"],
            },
        ],
    }
    result = parse(data)
    assert result == [
        NameData.person("輝夜姫", "かぐやひめ", source="jmnedict"),
        NameData.person("かぐや姫", "かぐやひめ", source="jmnedict"),
    ]
