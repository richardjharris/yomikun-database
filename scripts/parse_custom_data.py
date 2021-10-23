"""
Convert data/custom.csv (stdin) into JSONL (stdout)
"""
import sys

import csv
import regex
import logging

from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData

fields = ('kaki', 'yomi', 'tags', 'lifetime', 'notes')

# Remember last CSV input line, for error handling
last_raw_line = ''


def skip_lines_and_comments(lines):
    global last_raw_line

    for line in lines:
        last_raw_line = line.rstrip()
        line = regex.sub(r'#.*$', '', line)
        if regex.search(r'\S', line):
            yield line.rstrip()


# Skips comments and blank lines
reader = csv.DictReader(skip_lines_and_comments(sys.stdin), fields)
for row in reader:
    namedata = NameData(row['kaki'], row['yomi'])
    if row['tags']:
        tags = row['tags'].split('+')
        for tag in tags:
            if tag == 'm':
                namedata.set_gender('masc')
            elif tag == 'f':
                namedata.set_gender('fem')
            elif tag == 's':
                namedata.set_gender('surname')
            elif tag == 'pseudo':
                namedata.authenticity = NameAuthenticity.PSEUDO
            elif tag == 'fictional':
                namedata.authenticity = NameAuthenticity.FICTIONAL
            else:
                namedata.add_tag(tag)

    if namedata.is_person():
        namedata.add_tag('person')

    if row['lifetime']:
        try:
            birth, death = row['lifetime'].split('-')
        except ValueError:
            birth = row['lifetime']
            death = ''

        if len(birth):
            namedata.lifetime.birth_year = int(birth)
        if len(death):
            namedata.lifetime.death_year = int(death)

    if row['notes']:
        namedata.notes = row['notes']

    namedata.source = 'custom'

    # Normalise spaces
    namedata.clean()

    try:
        namedata.validate()
    except ValueError as e:
        logging.exception(
            f"Error parsing line '{last_raw_line}'\n"
            f"Generated dict: {row}\n"
            f"Generated namedata: {namedata}\n"
            f"Error: {e}")
        sys.exit(1)

    print(namedata.to_jsonl())
