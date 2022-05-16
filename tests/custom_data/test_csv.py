import io

import pytest

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
{"kaki": "二木 英徳", "yomi": "ふたぎ ひでのり", "authenticity": "real", "gender": "male", "position": "person", "lifetime": {"birth_year": 1936, "death_year": null}, "source": "custom", "notes": "Chairman (AEON)"}
{"kaki": "爽彩", "yomi": "さや", "authenticity": "real", "gender": "female", "position": "mei", "lifetime": {"birth_year": 2000, "death_year": null}, "source": "custom"}
{"kaki": "小田 剛嗣", "yomi": "おだ つよし", "authenticity": "real", "gender": "male", "position": "person", "lifetime": {"birth_year": 1920, "death_year": 1980}, "source": "custom"}
{"kaki": "宇治", "yomi": "うじ", "authenticity": "fictional", "position": "sei", "source": "custom"}
{"kaki": "白馬 弥那", "yomi": "はくば みな", "authenticity": "fictional", "gender": "female", "position": "person", "source": "custom"}
    """.strip()  # noqa
        + "\n"
    )


def test_error(caplog):
    input_data = io.StringIO("二木 英徳,ふたぎ　ひでのり,1936,m  # wrong-way around\n")
    output_data = io.StringIO()
    with pytest.raises(Exception, match="invalid tag '1936'"):
        csv.parse_file(input_data, output_data)
