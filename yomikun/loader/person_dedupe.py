from collections import defaultdict
import logging

from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData


class PersonDedupe():
    def __init__(self):
        self.people = defaultdict(list)

    def ingest(self, data: NameData):
        if not data.is_person():
            return

        key = (data.kaki, data.yomi, data.lifetime.birth_year)

        self.people[key].append(data)

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
            logging.debug(f'Single record, returning as-is')
            return people

        logging.debug(f'Merge')
        for i, person in enumerate(people):
            logging.debug(f"#{i+1}: {person}")

        # This is the return value
        merged = people[0].clone()

        # Dedupe logic
        genders = set(filter(None.__ne__, (p.gender() for p in people)))

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
            filter(None.__ne__, (p.lifetime.death_year for p in people)))
        if len(death_years) > 1:
            logging.info('Giving up (inconsistent death years)')
            return people
        elif len(death_years) == 1:
            merged.lifetime.death_year = death_years.pop()

        # Authenticity: if PSEUDO/FICTIONAL for any, all are
        not_real = set(
            p.authenticity for p in people if p.authenticity != NameAuthenticity.REAL)
        if len(not_real) > 1:
            logging.info('Giving up (pseudo vs fictional disagreement)')
            return people
        elif len(not_real) == 1:
            merged.authenticity = not_real.pop()

        # Copy over subreadings from the first record that contains them.
        for person in people:
            if person.subreadings:
                merged.subreadings = []
                for sub in person.subreadings:
                    merged.add_subreading(sub.clone())
                break

        # Pick a source
        merged.source = self.best_source(list(p.source for p in people))

        # Return the deduplicated record
        logging.info("Merged into 1 record")
        return [merged]

    preferred_sources = ('wikipedia_en', 'wikipedia_ja',
                         'wikidata', 'jmnedict', 'pdd')

    @classmethod
    def best_source(cls, sources: list[str]) -> str:
        for pref in cls.preferred_sources:
            for source in sources:
                if source == pref or source.startswith(pref + ':'):
                    return source
        else:
            return sources[0]


def test_preferred_sources():
    assert PersonDedupe.best_source([
        'daijisen:くろさわ‐あきら',
        'wikidata:http://www.wikidata.org/entity/Q95472952',
        'wikipedia_ja:黒沢明',
    ]) == 'wikipedia_ja:黒沢明'

    assert PersonDedupe.best_source(['jmnedict', 'custom']) == 'jmnedict'
