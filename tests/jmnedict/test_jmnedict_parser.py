from yomikun.models import Lifetime, NameData
from yomikun.models.name_position import NamePosition
from yomikun.parsers.jmnedict import parser


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
    result = parser.parse_jmnedict_entry(data)
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
    result = parser.parse_jmnedict_entry(data)
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
    result = parser.parse_jmnedict_entry(data)
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
    result = parser.parse_jmnedict_entry(data)
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
    result = parser.parse_jmnedict_entry(data)
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
    result = parser.parse_jmnedict_entry(data)
    expected = [
        NameData("愛", "ゆき", position=NamePosition.mei, is_dict=True, source="jmnedict"),
    ]
    assert result == expected, 'gender tag ignored, is_dict=True'

    # Test other tag combinations
    for name_types in (['given'], ['given', 'masc'], ['masc', 'fem']):
        data['senses'][0]['name_type'] = name_types
        assert parser.parse_jmnedict_entry(data) == expected, name_types


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
    result = parser.parse_jmnedict_entry(data)
    assert result == [
        NameData(
            "斎藤", "さいとう", position=NamePosition.sei, is_dict=True, source="jmnedict"
        ),
    ]


def test_surname_with_given_name():
    data = {
        "idseq": 5301123,
        "kanji": [{"text": "斎藤"}],
        "kana": [{"text": "さいとう", "nokanji": 0}],
        "senses": [
            {
                "SenseGloss": [{"lang": "eng", "text": "Saitou"}],
                "name_type": ["surname", "given"],
            }
        ],
    }
    result = parser.parse_jmnedict_entry(data)
    expected = [
        NameData(
            "斎藤", "さいとう", position=NamePosition.sei, is_dict=True, source="jmnedict"
        ),
        NameData(
            "斎藤", "さいとう", position=NamePosition.mei, is_dict=True, source="jmnedict"
        ),
    ]
    assert len(result) == 2
    assert (result == expected) or (result == expected[::-1])


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
    result = parser.parse_jmnedict_entry(data)
    assert result == [
        NameData.person("輝夜姫", "かぐやひめ", source="jmnedict"),
        NameData.person("かぐや姫", "かぐやひめ", source="jmnedict"),
    ]
