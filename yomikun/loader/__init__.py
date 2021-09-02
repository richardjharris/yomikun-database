"""
Data classes:
  Person(sei_kaki, mei_kaki, sei_yomi, mei_yomi, birth_year, death_year)
  Name:
    type: [SEI | MEI | UNCLAS]
    earliest_year: int
    latest_year: int
    real_count: int
    fictional_count: int
    pseudo_count: int
    top5k: bool
    gender: [M | F | N]
    source: str = (wikipedia highest priority, followed by others)

For each record:
  If record is a full name:
    - Add to Person table
    - Remember first lifetime seen, for reference

 - For each name part (if full name) or name entry (use tags):
   - Add to Name table
   - aggregate birth year range
   - increase sighting count (if not jmnedict, non-person)
       factoring in real/pen-name/fictional
   - mark as top5k if surname and in myoji-yurai list
   - mark gender (from jmnedict) if specified
"""


class Loader():
    def ingest(self, data: dict):
        pass

    def load(self):
        pass
