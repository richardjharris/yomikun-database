"""
Convert data/custom.yaml into JSONL
"""
import sys

import json
import yaml

from yomikun.models.namedata import NameData
from yomikun.models.lifetime import Lifetime

entries = yaml.load(sys.stdin, yaml.BaseLoader)
for entry in entries:
    namedata = NameData(entry['name'], entry['reading'])
    if 'lifetime' in entry:
        namedata.lifetime = Lifetime.from_string(entry['lifetime'])
    for tag in entry.get('tags', []):
        namedata.add_tag(tag)
    namedata.source = 'custom'

    print(namedata.to_jsonl())
