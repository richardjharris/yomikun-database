"""
Load the concatenated JSONL data produced by the various parser scripts
into an SQLite database.
"""

# TODO: jmnedict head
# TODO: wikipedia, subreadings

import sys
import json

import yomikun.loader
from yomikun.models import NameData

if __name__ == '__main__':
    aggregator = yomikun.loader.Aggregator()

    for line in sys.stdin:
        data = json.loads(line)

        # Remove orig, added by jmnedict parser
        if 'orig' in data:
            del data['orig']

        aggregator.ingest(NameData.from_dict(data))

    loader = yomikun.loader.Loader('temp.sqlite')
    loader.create_tables()
    for person in aggregator.people():
        loader.add_person(person)
    for name in aggregator.names():
        loader.add_name(name)
    loader.commit()
