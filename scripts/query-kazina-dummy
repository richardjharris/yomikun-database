"""
Queries kazina.com/dummy/ to generate random names, then tests to see if any
are missing from Yomikun's dataset.
"""
import csv
import sqlite3

import click
import requests

import yomikun.sqlite.query
from yomikun.models.gender import Gender
from yomikun.models.namedata import NameData
from yomikun.sqlite.models import NamePart

KAZINA_URL = 'http://kazina.com/dummy/dummy.cgi'


@click.command()
@click.argument('dbfile', type=click.Path(dir_okay=False), default='db/final.db')
@click.option(
    '--count', type=int, default=5000, help='Number of generated names to test.'
)
def query_kazina_dummay(dbfile, count):
    conn = sqlite3.connect(dbfile)

    r = requests.post(
        KAZINA_URL,
        data={
            'format': 'csv',
            'count': count,
            'name': 'l',
            'name_style': 'f g',
            'r': 1,
            'sex': 1,
            'sex_format': 'M|F',
        },
    )
    reader = csv.reader(r.text.splitlines())
    _ = next(reader)  # skip header
    for row in reader:
        kaki, yomi, gender_code = row
        gender = Gender.male if gender_code == 'M' else Gender.female
        namedata = NameData.person(kaki, yomi, gender=gender)

        for part in namedata.extract_name_parts():
            has_name = yomikun.sqlite.query.get_exact_match(
                conn,
                part.kaki,
                part.yomi,
                NamePart.from_position(part.position),
            )
            if not has_name:
                print("Missing: " + repr(part))


if __name__ == '__main__':
    query_kazina_dummay()
