"""
This script allows you to write custom.csv data in a lazier format,
for example:

八久保　竜司,ハチクボ　リュウジ
佐藤 直哉,さとう　なおや,m
頴川 文彦,Fumihiko Egawa,m+fictional

Katakana and romaji are converted to kana. (Must spell long vowels fully,
and for romaji, name order is Western by default)

Full names are split into given and surname components. These will be
tagged with either m, f or given (if no gender specified) or surname.
The data can then be sorted to anonymise the input.
"""
import csv
import sys
import regex

from yomikun.custom_data.importer import convert_to_hiragana
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData

fields = ('kaki', 'yomi', 'tags', 'lifetime', 'extra')

reader = csv.DictReader(sys.stdin, fields)

for row in reader:
    kaki = row['kaki']
    if not regex.match(r'^\p{Han}+(\s+\p{Han}+)?$', kaki):
        raise ValueError(f'Invalid kaki value {kaki}')

    yomi = convert_to_hiragana(row['yomi'])

    if len(kaki.split()) != len(yomi.split()):
        raise ValueError("kaki and yomi have different name counts")

    namedata = NameData(kaki, yomi)

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

    if row['lifetime']:
        birth, death = row['lifetime'].split('-')
        if len(birth):
            namedata.lifetime.birth_year = int(birth)
        if len(death):
            namedata.lifetime.death_year = int(death)

    namedata.source = 'custom'

    # Split person into two parts for anonymity
    if namedata.is_person():
        kaki_parts = namedata.kaki.split()
        yomi_parts = namedata.yomi.split()
        gender = namedata.gender()

        namedata.kaki, namedata.yomi = kaki_parts[1], yomi_parts[1]
        if not namedata.gender():
            namedata.add_tag('given')
        print(namedata.to_csv())

        namedata.kaki, namedata.yomi = kaki_parts[0], yomi_parts[0]
        namedata.remove_tag('given').add_tag('surname').set_gender(None)
        print(namedata.to_csv())
    else:
        print(namedata.to_csv())
