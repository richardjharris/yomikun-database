import csv
import logging
import sys
from typing import Optional, TextIO
import regex
from yomikun.custom_data.importer import convert_to_hiragana
from yomikun.models.nameauthenticity import NameAuthenticity
from yomikun.models.namedata import NameData

# CSV field names
csv_fields = ('kaki', 'yomi', 'tags', 'lifetime', 'notes')

# Remember last CSV input line, for error handling
last_raw_line = ''
last_raw_line_number = 0

def parse_file(input_file: TextIO, output_file: TextIO, input_filename: Optional[str] = None):
    """
    Parse a CSV file and write JSONL output.

    If an error is encountered, displays contextual information and exits
    the program.
    """
    reader = csv.DictReader(skip_lines_and_comments(input_file), csv_fields)
    for row in reader:
        namedata = None
        try:
            namedata = parse_row(row)
            namedata.validate()
            print(namedata.to_jsonl(), file=output_file)
        except ValueError as e:
            location = f"line {last_raw_line_number}"
            if input_filename:
                location = f"file '{input_filename}' {location}"

            logging.exception(
                f"Error parsing {location}\n"
                f"Error: {e}\n\n"
                f"Raw line: {last_raw_line}\n"
                f"Generated dict: {row}\n"
                f"Generated namedata: {namedata}"
            )
            sys.exit(1)

def skip_lines_and_comments(lines):
    global last_raw_line
    global last_raw_line_number

    last_raw_line_number = 0

    for line in lines:
        last_raw_line = line.rstrip()
        last_raw_line_number += 1
        line = regex.sub(r'#.*$', '', line)
        if regex.search(r'\S', line):
            yield line.rstrip()


def parse_row(row: dict) -> NameData:
    """
    Parse an incoming CSV data row and return a NameData object.
    """
    kaki = row['kaki']
    yomi = convert_to_hiragana(row['yomi'])
    namedata = NameData(kaki, yomi)

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
            elif tag in ('fictional', 'fict'):
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
    return namedata
