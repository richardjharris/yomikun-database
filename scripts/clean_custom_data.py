"""
Script to be run against new custom.csv-type data before it is
appended to custom.csv.

 - convert katakana and romaji names to kana
 - split names into surname + given name components, which can
   then be shuffled to anonymise the data.
"""
import csv
import sys
import regex

from yomikun.custom_data.importer import convert_to_hiragana

fields = ('kaki', 'yomi', 'tags', 'lifetime', 'extra')

reader = csv.DictReader(sys.stdin, fields)

for row in reader:
    kaki = row['kaki']
    if not regex.match(r'^\p{Han}+(\s+\p{Han}+)?$', kaki):
        raise ValueError(f'Invalid kaki value {kaki}')

    yomi = convert_to_hiragana(row['yomi'])

    assert len(kaki.split()) == len(yomi.split())

    if len(kaki.split()) == 2:
        # This is a person record
        tags = row["tags"]
        lifetime = row["lifetime"]

        # TBD

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
