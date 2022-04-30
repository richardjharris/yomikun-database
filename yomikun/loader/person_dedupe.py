from collections import defaultdict
import logging

from yomikun.models import Lifetime

from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData


class PersonDedupe:
    def __init__(self):
        self.people = defaultdict(list)

    def ingest(self, data: NameData) -> bool:
        """
        For people records, returns True and ingests the data.
        For other records, returns False and ignores it.
        """
        if not data.is_person():
            return False

        key = (data.kaki, data.yomi, data.lifetime.birth_year)

        self.people[key].append(data)
        return True

    def deduped_people(self):
        """
        Returns a generator that outputs de-duplicated people
        as NameData records.
        """
        for dupe_set in self.people.values():
            yield from self.dedupe(dupe_set)

    def dedupe(self, people: list[NameData]) -> list[NameData]:
        """
        Given input [A, B, C] returns either a deduped [A']
        that merges data from the other person records, or returns
        [A, B, C] unchanged if de-duplication is not possible.

        Assumes the kaki, yomi and birth year are the same for all
        input records.
        """

        if len(people) == 1:
            logging.debug("Single record, returning as-is")
            return people

        logging.debug("Merge:")
        for i, person in enumerate(people):
            logging.debug(f"#{i+1}: {person}")

        # This is the return value
        merged = people[0].clone()

        # Dedupe logic
        genders = set(p.gender() for p in people if p.gender() is not None)

        if len(genders) > 1:
            logging.info('Giving up (inconsistent genders)')
            return people
        elif len(genders) == 1:
            gender = genders.pop()
            assert isinstance(gender, str)  # shut pyright up
            merged.set_gender(gender)

        # All people have the same birth_year, but fill in death_year if
        # missing.
        death_years = set(
            p.lifetime.death_year for p in people if p.lifetime.death_year is not None
        )
        if len(death_years) > 1:
            logging.info('Giving up (inconsistent death years)')
            return people
        elif len(death_years) == 1:
            merged.lifetime.death_year = death_years.pop()

        # Authenticity: if PSEUDO/FICTIONAL for any, all are
        not_real = set(
            p.authenticity for p in people if p.authenticity != NameAuthenticity.REAL
        )
        if len(not_real) > 1:
            logging.info('Giving up (pseudo vs fictional disagreement)')
            return people
        elif len(not_real) == 1:
            merged.authenticity = not_real.pop()

        # Copy over subreadings from the first record that contains them.
        # TODO may be interesting to dedupe the subreadings also??
        # TODO or at least check if we've missed some
        for person in people:
            if person.subreadings:
                merged.subreadings = []
                for sub in person.subreadings:
                    merged.add_subreading(sub.clone())
                break

        # Pick a source
        merged.source = self.best_source(list(p.source for p in people))

        # Pick notes
        all_notes = [(p.source, p.notes) for p in people if p.notes]
        if len(all_notes):
            # use wikipedia_en field in preference
            all_notes.sort(key=lambda x: x[0].startswith('wikipedia_en:'), reverse=True)
            merged.notes = all_notes[0][1]

        # Remove xx-romaji if at least one record does not have it
        if any(not p.has_tag('xx-romaji') for p in people):
            merged.remove_tag('xx-romaji')

        # Return the deduplicated record
        logging.info("Merged into 1 record")
        return [merged]

    preferred_sources = ('wikipedia_en', 'wikipedia_ja', 'wikidata', 'jmnedict', 'pdd')

    @classmethod
    def best_source(cls, sources: list[str]) -> str:
        for pref in cls.preferred_sources:
            for source in sources:
                if source == pref or source.startswith(pref + ':'):
                    return source
        else:
            return sources[0]


def test_preferred_sources():
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


def test_akira():
    jsonl = """
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "jmnedict", "tags": ["person"]}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikidata:http://www.wikidata.org/entity/Q8006", "tags": ["person", "masc"], "notes": "日本の映画監督"}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikipedia_en:Akira Kurosawa", "tags": ["xx-romaji", "masc", "person"], "notes": "Filmmaker and painter who directed 30 films in a career spanning 57 years"}
{"kaki": "黒澤 明", "yomi": "くろさわ あきら", "authenticity": "real", "lifetime": {"birth_year": 1910, "death_year": 1998}, "source": "wikipedia_ja:黒澤明", "tags": ["person"]}
    """.strip()  # noqa: E501

    pd = PersonDedupe()
    for person in jsonl.splitlines():
        pd.ingest(NameData.from_jsonl(person))

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
