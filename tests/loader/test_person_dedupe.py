import pytest

from yomikun.loader.person_dedupe import PersonDedupe
from yomikun.models import Lifetime, NameData
from yomikun.models.nameauthenticity import NameAuthenticity as NA


def test_akira():
    """Basic test of deduping four real-world Akira Kurosawa entries."""
    jsonl = """
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "jmnedict", "tags": ["person"]}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikidata:http://www.wikidata.org/entity/Q8006", "tags": ["person", "masc"], "notes": "日本の映画監督"}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikipedia_en:Akira Kurosawa", "tags": ["xx-romaji", "masc", "person"], "notes": "Filmmaker and painter who directed 30 films in a career spanning 57 years"}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikipedia_ja:黒澤明", "tags": ["person"]}
    """.strip()  # noqa: E501

    pd = PersonDedupe()
    for person in jsonl.splitlines():
        assert pd.ingest(NameData.from_jsonl(person))

    people = list(pd.deduped_people())
    assert len(people) == 1

    assert people[0] == NameData.person(
        '黒澤 明',
        'くろさわ あきら',
        lifetime=Lifetime(1910, 1998),
        source='wikipedia_en:Akira Kurosawa',
        tags=['person', 'masc'],
        notes='Filmmaker and painter who directed 30 films in a career spanning 57 years',
    )


def test_natsume():
    """Test that involves copying subreadings and dealing with real/pseudo"""
    jsonl = """
{"kaki": "夏目 漱石", "yomi": "なつめ そうせき", "authenticity": "real", "lifetime": {"birth_year": 1867, "death_year": 1916}, "subreadings": [], "source": "daijisen:なつめ‐そうせき【夏目漱石】", "tags": ["person"]}
{"kaki": "夏目 漱石", "yomi": "なつめ そうせき", "authenticity": "real", "lifetime": {"birth_year": 1867, "death_year": 1916}, "subreadings": [], "source": "koujien:なつめ‐そうせき【夏目漱石】", "tags": ["person"]}
{"kaki": "夏目 漱石", "yomi": "なつめ そうせき", "authenticity": "pseudo", "lifetime": {"birth_year": 1867, "death_year": 1916}, "subreadings": [{"kaki": "夏目 金之助", "yomi": "なつめ きんのすけ", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "", "tags": ["person"], "notes": ""}], "source": "wikipedia_ja:夏目漱石", "tags": ["person"]}
    """.strip()  # noqa: E501

    pd = PersonDedupe()
    for person in jsonl.splitlines():
        assert pd.ingest(NameData.from_jsonl(person))

    people = list(pd.deduped_people())
    assert len(people) == 1

    assert people[0] == NameData.person(
        '夏目 漱石',
        'なつめ そうせき',
        lifetime=Lifetime(1867, 1916),
        authenticity=NA.PSEUDO,  # from third result
        source='wikipedia_ja:夏目漱石',
        tags=['person'],
        subreadings=[
            NameData.person(
                '夏目 金之助',
                'なつめ きんのすけ',
            ),
        ],
    )


def test_non_person_dedupe():
    pd = PersonDedupe()
    assert pd.ingest(NameData("心愛", "ここあ", tags={'fem'})) is False, 'ignored'
    assert not list(pd.deduped_people()), 'no results returned'


def test_single_dedupe():
    person = NameData("大野 心愛", "おおの ここあ", tags={'person'})
    pd = PersonDedupe()
    assert pd.ingest(person)
    assert list(pd.deduped_people()) == [person], 'single result returned'


def test_multiple_genders():
    """Should not dedupe if genders are different."""
    person1 = NameData('田中 ひびき', 'たなか ひびき', tags={'masc'})
    person2 = person1.clone().set_gender('fem')
    pd = PersonDedupe()
    assert pd.ingest(person1)
    assert pd.ingest(person2)
    assert list(pd.deduped_people()) == [person1, person2], 'no dedupe performed'


def test_multiple_death_years():
    """Should not dedupe if death years are different"""
    person1 = NameData(
        '田中 ひびき', 'たなか ひびき', tags={'masc'}, lifetime=Lifetime(1910, 1998)
    )
    person2 = person1.clone()
    person2.lifetime.death_year = 1999
    pd = PersonDedupe()
    assert pd.ingest(person1)
    assert pd.ingest(person2)
    assert list(pd.deduped_people()) == [person1, person2], 'no dedupe performed'


def test_pseudo_fictional_different():
    """
    If there are a mix of authenticities, the logic is:
     1) all real -> merge as real
     2) real + non-real -> merge as the non-real
        This assumes the 'real' entry was incorrectly marked as real because we
        failed to extract a pen- or stagename.
     3) all non-real -> merge unless they are different types

     Returns NameAuthenticity of merged data if merged, else None.
    """

    def merged_ok(type1: NA, type2: NA) -> NA | None:
        person1 = NameData('田中 ひびき', 'たなか ひびき', authenticity=type1)
        person2 = person1.clone()
        person2.authenticity = type2
        pd = PersonDedupe()
        pd.ingest(person1)
        pd.ingest(person2)
        result = list(pd.deduped_people())
        if len(result) == 1:
            return result[0].authenticity
        elif len(result) == 2:
            return None  # not merged
        else:
            raise Exception('unexpected result')

    assert merged_ok(NA.REAL, NA.REAL) == NA.REAL
    assert merged_ok(NA.REAL, NA.PSEUDO) == NA.PSEUDO
    assert merged_ok(NA.PSEUDO, NA.REAL) == NA.PSEUDO
    assert merged_ok(NA.PSEUDO, NA.PSEUDO) == NA.PSEUDO
    assert merged_ok(NA.PSEUDO, NA.FICTIONAL) is None
    assert merged_ok(NA.FICTIONAL, NA.PSEUDO) is None
    assert merged_ok(NA.FICTIONAL, NA.FICTIONAL) == NA.FICTIONAL
    assert merged_ok(NA.FICTIONAL, NA.REAL) == NA.FICTIONAL


def test_preferred_sources():
    """Test that `best_source` prefers the correct sources."""
    assert (
        PersonDedupe.best_source(
            [
                'daijisen:くろさわ‐あきら',
                'wikidata:http://www.wikidata.org/entity/Q95472952',
                'wikipedia_ja:黒沢明',
            ]
        )
        == 'wikipedia_ja:黒沢明'
    )

    assert PersonDedupe.best_source(['jmnedict', 'custom']) == 'jmnedict'
    assert PersonDedupe.best_source(['custom', 'jmnedict']) == 'jmnedict'
    assert PersonDedupe.best_source(['custom']) == 'custom', 'single source'

    with pytest.raises(IndexError):
        PersonDedupe.best_source([])
