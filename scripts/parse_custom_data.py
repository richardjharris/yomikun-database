"""
Convert data/custom.csv (stdin) into JSONL (stdout)
"""
import sys

import csv
import regex

from yomikun.models.nameauthenticity import NameAuthenticity

from yomikun.models.namedata import NameData


fields = ('kaki', 'yomi', 'tags', 'lifetime', 'extra')

reader = csv.DictReader(sys.stdin, fields)
for row in reader:
    if not regex.match(r'^\p{Han}+(\s+\p{Han}+)?$', row['kaki']):
        raise ValueError(f'Invalid kaki value {row["kaki"]}')

    namedata = NameData(row['kaki'], row['yomi'])
    if row['tags']:
        tags = row['tags'].split('+')
        for tag in tags:
            if tag == 'm':
                namedata.set_gender('masc')
            elif tag == 'f':
                namedata.set_gender('fem')
            elif tag == 'pseudo':
                namedata.authenticity = NameAuthenticity.PSEUDO
            elif tag == 'fictional':
                namedata.authenticity = NameAuthenticity.FICTIONAL
            else:
                namedata.add_tag(tag)

    if namedata.is_person():
        namedata.add_tag('person')

    if row['lifetime']:
        birth, death = row['lifetime'].split('-')
        if len(birth):
            namedata.lifetime.birth_year = int(birth)
        if len(death):
            namedata.lifetime.death_year = int(death)

    namedata.source = 'custom'

    print(namedata.to_jsonl())
