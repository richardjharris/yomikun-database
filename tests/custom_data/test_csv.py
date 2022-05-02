import io

from yomikun.custom_data import csv


def test_success():
    input_data = io.StringIO(
        """
# Comment, ignored

# Blank lines also ignored
二木 英徳,ふたぎ　ひでのり,m,1936,Chairman (AEON)
爽彩,さや,f,2000-
小田　剛嗣,おだ つよし,m,1920-1980 # Based on Coke can in FB profile
宇治,うじ,s+fictional
白馬 弥那,はくば　みな,f+fict
    """.strip()
    )
    output_data = io.StringIO()

    csv.parse_file(input_data, output_data)

    assert (
        output_data.getvalue()
        == """
{"kaki": "二木 英徳", "yomi": "ふたぎ ひでのり", "authenticity": "real", "lifetime": {"birth_year": 1936, "death_year": null}, "source": "custom", "tags": ["masc", "person"], "notes": "Chairman (AEON)"}
{"kaki": "爽彩", "yomi": "さや", "authenticity": "real", "lifetime": {"birth_year": 2000, "death_year": null}, "source": "custom", "tags": ["fem"]}
{"kaki": "小田 剛嗣", "yomi": "おだ つよし", "authenticity": "real", "lifetime": {"birth_year": 1920, "death_year": 1980}, "source": "custom", "tags": ["masc", "person"]}
{"kaki": "宇治", "yomi": "うじ", "authenticity": "fictional", "source": "custom", "tags": ["surname"]}
{"kaki": "白馬 弥那", "yomi": "はくば みな", "authenticity": "fictional", "source": "custom", "tags": ["fem", "person"]}
    """.strip()  # noqa
        + "\n"
    )


def test_error(caplog):
    input_data = io.StringIO("二木 英徳,ふたぎ　ひでのり,1936,m  # wrong-way around\n")
    output_data = io.StringIO()

    assert not csv.parse_file(input_data, output_data)
    assert output_data.getvalue() == ""
    assert caplog.records[0].levelname == "ERROR"
    assert (
        "Error: invalid literal for int() with base 10: 'm'"
        in caplog.records[0].message
    )
