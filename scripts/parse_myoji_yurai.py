"""
Parses myoji-yurai-readings.csv data to get top 5000
Japanese surnames and their 'typical' readings.
"""
from __future__ import annotations
from typing import Iterable
import sys
import regex

from models import NameType, NameData, Lifetime


def parse_myoji_yurai(lines: Iterable[str]):
    for line in lines:
        line.strip()
        # population = e.g. 1894000 for 佐藤
        # difficulty = ranging from 0.5ish (easy) to 1000+, although it is
        #              pretty unreliable for long names
        kanji, readings_joined, _population, _difficulty = line.split(',')
        readings = readings_joined.split('|')

        for reading in readings:
            data = NameData(kanji, reading)
            # TBD
            pass


if __name__ == '__main__':
    parse_myoji_yurai(sys.stdin.readlines())
